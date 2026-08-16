package com.shatteredpixel.shatteredpixeldungeon.agent.jacocoReporter;

import java.io.File;
import java.io.IOException;

/**
 * Example usage of JacocoXmlReportGenerator.
 * Demonstrates various ways to generate XML reports from exec files.
 */
public class XmlReportGeneratorExample {

    public static void main(String[] args) {
        try {
            System.out.println("=== JaCoCo XML Report Generator - Examples ===\n");

            // Example 1: Generate all reports (every file)
            example1_GenerateAllReports();

            // Example 2: Generate reports with interval jump
            example2_GenerateWithInterval();

            // Example 3: Custom directory
            example3_CustomDirectory();

            // Example 4: Advanced configuration
            example4_AdvancedConfiguration();

            // Example 5: Save exclusion lists
            example5_SaveExclusionLists();

            // Example 6: Generate a single report
            example6_SingleReport();

            // Example 7: Full workflow
            example7_FullWorkflow();

            // Example 8: Time range processing
            example8_TimeRangeProcessing();

            // Example 9: Verify exclusions are working (NEW)
            example9_VerifyExclusions();

            // Example 10: Generate report with statistics (NEW)
            example10_GenerateWithStatistics();

            System.out.println("\n=== All Examples Completed ===");

        } catch (IOException e) {
            System.err.println("Error generating reports: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Example 1: Generate XML reports for all exec files.
     * Uses default configuration with interval jump of 1 (every file).
     */
    private static void example1_GenerateAllReports() throws IOException {
        System.out.println("\n=== Example 1: Generate All Reports ===");

        // Simple one-liner to generate reports for all files
        JacocoXmlReportGenerator.generateAllReports();

        System.out.println("All reports generated successfully!");
    }

    /**
     * Example 2: Generate XML reports for every Nth file.
     * Useful for large datasets where processing every file is too slow.
     */
    private static void example2_GenerateWithInterval() throws IOException {
        System.out.println("\n=== Example 2: Generate Reports with Interval Jump ===");

        // Generate report for every 5th file
        int intervalJump = 5;
        JacocoXmlReportGenerator.generateReports(intervalJump);

        System.out.println("Reports generated for every " + intervalJump + " files!");
    }

    /**
     * Example 3: Generate reports from a custom directory.
     * Useful when exec files are in a non-default location.
     */
    private static void example3_CustomDirectory() throws IOException {
        System.out.println("\n=== Example 3: Custom Directory ===");

        // Specify custom exec directory
        File execDir = new File("../../out/SPD/jacoco-reports/CustomAgent");

        if (!execDir.exists()) {
            System.out.println("Custom directory does not exist, skipping example 3");
            return;
        }

        JacocoXmlReportGenerator.generateReports(execDir);

        System.out.println("Reports generated from custom directory!");
    }

    /**
     * Example 4: Advanced configuration using the builder pattern.
     * Provides full control over all settings including custom exclusions.
     */
    private static void example4_AdvancedConfiguration() throws IOException {
        System.out.println("\n=== Example 4: Advanced Configuration ===");

        // Build custom configuration
        JacocoXmlReportGenerator.ReportConfig config =
                new JacocoXmlReportGenerator.ReportConfigBuilder()
                        .execDir("../../out/SPD/jacoco-reports/MyAgent")
                        .xmlOutputDir("../../out/SPD/custom-xml-reports")
                        .classesDir("../../core/build/classes/java/main")
                        .intervalJump(10) // Every 10th file
                        .addExcludedPackage("com/myproject/test/") // Add custom exclusion
                        .addExcludedClass("com/myproject/DebugUtil") // Add custom class exclusion
                        .build();

        // Check if directories exist
        if (!config.execDir.exists()) {
            System.out.println("Exec directory does not exist, skipping example 4");
            return;
        }

        // Generate reports with custom config
        JacocoXmlReportGenerator.generateReports(config);

        System.out.println("Reports generated with custom configuration!");
    }

    /**
     * Example 5: Save exclusion lists to files.
     * Useful for documentation and sharing exclusion configurations.
     */
    private static void example5_SaveExclusionLists() throws IOException {
        System.out.println("\n=== Example 5: Save Exclusion Lists ===");

        // Save to default location
        JacocoXmlReportGenerator.saveExclusionLists();

        // Or save to custom location
        File customDir = new File("../../out/SPD/documentation");
        if (!customDir.exists() && !customDir.mkdirs()) {
            System.out.println("Failed to create custom directory");
            return;
        }
        JacocoXmlReportGenerator.saveExclusionLists(customDir);

        System.out.println("Exclusion lists saved!");
        System.out.println("- excluded_packages.txt");
        System.out.println("- excluded_classes.txt");
    }

    /**
     * Example 6: Generate a single report for a specific exec file.
     * Useful for testing or processing specific files.
     */
    private static void example6_SingleReport() throws IOException {
        System.out.println("\n=== Example 6: Single Report Generation ===");

        File execFile = new File("../../out/SPD/jacoco-reports/MyAgent/MyAgent_26_08_15_1000.exec");
        File xmlFile = new File("../../out/SPD/jacoco-xml-reports/single_report.xml");

        if (!execFile.exists()) {
            System.out.println("Exec file does not exist, skipping example 6");
            return;
        }

        // Ensure output directory exists
        File xmlDir = xmlFile.getParentFile();
        if (!xmlDir.exists() && !xmlDir.mkdirs()) {
            throw new IOException("Failed to create XML output directory");
        }

        // Generate single report
        JacocoXmlReportGenerator.ReportConfig config =
                new JacocoXmlReportGenerator.ReportConfigBuilder().build();

        JacocoXmlReportGenerator.generateSingleReport(execFile, xmlFile, config);

        System.out.println("Single report generated: " + xmlFile.getName());
    }

    /**
     * Example 7: Full workflow - collect coverage and generate reports.
     * Demonstrates typical usage in a test or research scenario.
     */
    private static void example7_FullWorkflow() throws IOException {
        System.out.println("\n=== Example 7: Full Workflow ===");

        // Step 1: During gameplay, coverage is dumped automatically by JacocoRuntimeReporter
        // (This happens in your game code)
        System.out.println("Step 1: Coverage data collected during gameplay");
        System.out.println("  - JacocoRuntimeReporter.dumpData() called for each action");
        System.out.println("  - Exec files saved to: ../../out/SPD/jacoco-reports/");

        // Step 2: After gameplay, generate XML reports
        System.out.println("\nStep 2: Generate XML reports");
        int intervalJump = 5; // Process every 5th file for performance
        JacocoXmlReportGenerator.generateReports(intervalJump);

        // Step 3: Save exclusion lists for documentation
        System.out.println("\nStep 3: Save exclusion lists");
        JacocoXmlReportGenerator.saveExclusionLists();

        // Step 4: XML reports are now ready for analysis
        System.out.println("\nStep 4: Analysis");
        System.out.println("  - XML reports can be imported into SonarQube, Jenkins, etc.");
        System.out.println("  - Or processed with custom analysis tools");

        System.out.println("\nWorkflow completed successfully!");
    }

    /**
     * Example 8: Processing specific time range.
     * Shows how to filter exec files by timestamp before generating reports.
     */
    private static void example8_TimeRangeProcessing() throws IOException {
        System.out.println("\n=== Example 8: Time Range Processing ===");

        // This is a conceptual example showing how you might filter files
        // before processing them with the generator

        File execDir = new File("../../out/SPD/jacoco-reports/MyAgent");
        if (!execDir.exists()) {
            System.out.println("Exec directory does not exist, skipping example 8");
            return;
        }

        // Get all exec files
        File[] allFiles = execDir.listFiles((dir, name) ->
                name.endsWith(".exec") && !name.contains("_delta.exec"));

        if (allFiles == null || allFiles.length == 0) {
            System.out.println("No exec files found");
            return;
        }

        System.out.println("Found " + allFiles.length + " exec files");
        System.out.println("You could filter these by timestamp in the filename");
        System.out.println("Then process only the filtered files");

        // For full processing of filtered files, you would:
        // 1. Filter files by your criteria (timestamp, etc.)
        // 2. Copy them to a temp directory
        // 3. Run generateReports on that directory
        // or
        // 1. Process each file individually with generateSingleReport
    }

    /**
     * Example 9: Verify exclusions are working correctly.
     * Demonstrates the new printExclusionSummary() method.
     */
    private static void example9_VerifyExclusions() {
        System.out.println("\n=== Example 9: Verify Exclusions ===");

        // Print what packages and classes are excluded
        JacocoXmlReportGenerator.printExclusionSummary();

        System.out.println("The above exclusions are applied during analysis.");
        System.out.println("This means when you fetch total coverage from XML reports,");
        System.out.println("these packages/classes are NOT included in the totals.");
        System.out.println("No post-processing needed!");
    }

    /**
     * Example 10: Generate report with statistics to verify totals.
     * Demonstrates the new generateSingleReportWithStats() method.
     * This is useful to confirm that exclusions are properly applied to totals.
     */
    private static void example10_GenerateWithStatistics() throws IOException {
        System.out.println("\n=== Example 10: Generate Report with Statistics ===");

        // Find any exec file in the default directory
        File execDir = new File("../../out/SPD/jacoco-reports");
        if (!execDir.exists()) {
            System.out.println("Exec directory does not exist, skipping example 10");
            return;
        }

        // Try to find the agent subdirectory
        File[] agentDirs = execDir.listFiles(File::isDirectory);
        if (agentDirs == null || agentDirs.length == 0) {
            System.out.println("No agent directories found, skipping example 10");
            return;
        }

        File agentDir = agentDirs[0]; // Use first agent directory
        File[] execFiles = agentDir.listFiles((dir, name) -> 
            name.endsWith(".exec") && !name.contains("_delta.exec"));

        if (execFiles == null || execFiles.length == 0) {
            System.out.println("No exec files found in " + agentDir.getName());
            System.out.println("Skipping example 10");
            return;
        }

        // Use the first exec file
        File execFile = execFiles[0];
        File xmlFile = new File("../../out/SPD/jacoco-xml-reports/example_with_stats.xml");

        // Ensure output directory exists
        File xmlDir = xmlFile.getParentFile();
        if (!xmlDir.exists() && !xmlDir.mkdirs()) {
            throw new IOException("Failed to create XML output directory");
        }

        // Generate report with statistics
        JacocoXmlReportGenerator.ReportConfig config = 
            new JacocoXmlReportGenerator.ReportConfigBuilder().build();

        System.out.println("Generating report for: " + execFile.getName());
        JacocoXmlReportGenerator.generateSingleReportWithStats(execFile, xmlFile, config);

        System.out.println("\nThe statistics shown above are AFTER exclusions are applied.");
        System.out.println("When you parse the XML to fetch totals, you'll get the same numbers.");
        System.out.println("This confirms that exclusions affect the total coverage calculations!");
    }
}

