import re
import json

def parse_result_prediction_str(
        result_prediction_str: str
) -> dict:
    """
    Parses a string representation of a Prediction(...) object and extracts attributes,
    including list fields and integers.

    :param result_prediction_str: A string like 'Prediction(...)'
    :return: A dictionary of parsed fields suitable for initializing a ResultPrediction object.
    """
    # Extract simple string fields
    attrs = dict(re.findall(r"(\w+)\s*=\s*['\"]([^'\"]*?)['\"]", result_prediction_str))

    # Handle complex list fields like items=["..."]
    list_fields = ["items"]
    for key in list_fields:
        match = re.search(rf"{key}\s*=\s*['\"](\[.*?\])['\"]", result_prediction_str, re.DOTALL)
        if match:
            try:
                attrs[key] = json.loads(match.group(1))
            except json.JSONDecodeError:
                attrs[key] = []
        else:
            attrs[key] = []

    # Convert known numeric fields
    if "quantity" in attrs:
        try:
            attrs["quantity"] = int(attrs["quantity"])
        except ValueError:
            attrs["quantity"] = 0

    return attrs  # or ResultPrediction(**attrs) if using directly


def parse_code_str(
        prediction_str: str
) -> dict:
    """
    Parses a string representation of a Prediction(...) object to extract code, skills, and other fields.
    :param prediction_str: A string like 'Prediction(...)' containing code and skills.
    :return: A dictionary with keys 'code', 'used_skills_name', and other string fields.
    """
    # Extract everything inside Prediction(...)
    match = re.search(r"Prediction\s*\((.*)\)", prediction_str, re.DOTALL)
    if not match:
        raise ValueError("Could not extract Prediction() block from string")

    content = match.group(1)

    # Extract raw 'code' field (string with escaped newlines)
    code_field_match = re.search(r"code\s*=\s*(['\"])(.*?)\1", content, re.DOTALL)
    code_block = code_field_match.group(2) if code_field_match else ""

    # Unescape escaped newlines for clean parsing
    unescaped_code_block = code_block.encode('utf-8').decode('unicode_escape')

    # Extract code inside triple backticks
    inner_code_match = re.search(r"```(?:javascript)?\n?(.*?)```", unescaped_code_block, re.DOTALL)
    code = inner_code_match.group(1).strip() if inner_code_match else ""

    # Extract used_skills_name as a list (JSON format or plain string)
    skills_match = re.search(r"used_skills_name\s*=\s*['\"](\[.*?\])['\"]", content, re.DOTALL)
    try:
        used_skills_name = json.loads(skills_match.group(1)) if skills_match else []
    except json.JSONDecodeError:
        used_skills_name = []

    # Remove "code='```...```'", to avoid confusion in further parsing
    content = re.sub(r"code\s*=\s*(['\"])(.*?)\1", "code='[CODE_BLOCK]'", content, flags=re.DOTALL)

    # print("Content after code replacement:", content)

    # Extract all other string fields (excluding the special fields)
    fields = dict(re.findall(r"(\w+)\s*=\s*['\"]((?:(?!```)[^'\"])+)['\"]", content))
    fields["code"] = code
    fields["used_skills_name"] = used_skills_name

    return fields


if __name__ == "__main__":
    # Test
    test_str = '''Prediction(
    reasoning='To start progressing towards crafting tools and eventually shearing a sheep, I need to gather some basic resources. The nearby blocks include oak logs, which are essential for crafting a crafting table and other wooden tools. Since my inventory is currently empty, I should focus on collecting oak logs first. This will allow me to craft a crafting table and then proceed with crafting other necessary items.',
    code_design='1. Check if I have at least 3 oak logs in my inventory. If yes, return.\n2. If not, find a nearby oak log block.\n3. Use the `mineBlock` function to mine the oak log block.\n4. Repeat the process until I have collected 3 oak logs in my inventory.',
    skill_name='collectOakLogs',
    used_skills_name='["mineBlock"]',
    code='```javascript\nasync function collectOakLogs(bot, mcData) {\n    const oakLogName = "oak_log";\n    const requiredCount = 3;\n\n    // Check if we already have enough oak logs\n    const inventoryCount = bot.inventory.count(mcData.itemsByName[oakLogName].id);\n    if (inventoryCount >= requiredCount) {\n        bot.chat("Already have enough oak logs.");\n        return;\n    }\n\n    // Find and mine oak logs until we have enough\n    while (bot.inventory.count(mcData.itemsByName[oakLogName].id) < requiredCount) {\n        const oakLogBlock = bot.findBlock({\n            matching: mcData.blocksByName[oakLogName].id,\n            maxDistance: 32\n        });\n\n        if (!oakLogBlock) {\n            bot.chat("No oak logs nearby, exploring...");\n            await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {\n                return bot.findBlock({\n                    matching: mcData.blocksByName[oakLogName].id,\n                    maxDistance: 32\n                });\n            });\n        }\n\n        await mineBlock(bot, mcData, oakLogName, 1);\n        bot.chat(`Collected ${bot.inventory.count(mcData.itemsByName[oakLogName].id)} oak logs.`);\n    }\n}\n```',
    code_failing_reason='There is no failing reason for the code as it is designed to handle the task of collecting oak logs efficiently by checking the inventory and using the `mineBlock` function to gather the required resources.'
    )'''

    parsed = parse_code_str(test_str)
    print(parsed)
