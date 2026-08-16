package com.shatteredpixel.shatteredpixeldungeon.agent.jacocoReporter;

import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.IBundleCoverage;
import org.jacoco.core.analysis.ICounter;
import org.jacoco.core.data.ExecutionDataStore;
import org.jacoco.core.tools.ExecFileLoader;

import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Exports JaCoCo coverage data to CSV format.
 * Fetches coverage data from exec files and writes to CSV with action counter correlation.
 */
public final class JacocoCoverageCsvExporter {

    private static final String AGENT_NAME = "agentAggression1";
    
    // Default paths
    private static final String DEFAULT_EXEC_DIR = "../out/SPD/jacoco-reports/" + AGENT_NAME;
    private static final String DEFAULT_CSV_OUTPUT_PATH = "../out/SPD/jacoco-coverage-csv/" + AGENT_NAME + "_coverage.csv";
    private static final String DEFAULT_CLASSES_DIR = "./core/build/classes/java/main";
    private static final String DEFAULT_JSONL_DIR = "../out/SPD/jacoco-reports-action-jsonl";

    // Exclusions (same as JacocoXmlReportGenerator)
    private static final List<String> EXCLUDED_PACKAGES = Arrays.asList(
            "com/shatteredpixel/shatteredpixeldungeon/agent/",
            "com/shatteredpixel/shatteredpixeldungeon/APIs/",
            "com/shatteredpixel/shatteredpixeldungeon/journal/",
            "com/shatteredpixel/shatteredpixeldungeon/messages/",
            "com/shatteredpixel/shatteredpixeldungeon/plants/",
            "com/shatteredpixel/shatteredpixeldungeon/services/news/",
            "com/shatteredpixel/shatteredpixeldungeon/services/updates/",
            "com/shatteredpixel/shatteredpixeldungeon/scenes/",
            "com/shatteredpixel/shatteredpixeldungeon/ui/",
            "com/shatteredpixel/shatteredpixeldungeon/windows/",
            "com/shatteredpixel/shatteredpixeldungeon/utils/"
    );

    private static final List<String> EXCLUDED_CLASSES = Arrays.asList(
            "com/shatteredpixel/shatteredpixeldungeon/Challenges",
            "com/shatteredpixel/shatteredpixeldungeon/Chrome",
            "com/shatteredpixel/shatteredpixeldungeon/Dungeon",
            "com/shatteredpixel/shatteredpixeldungeon/GamesInProgress",
            "com/shatteredpixel/shatteredpixeldungeon/actors/hero/HeroAction",
            "com/shatteredpixel/shatteredpixeldungeon/QuickSlot",
            "com/shatteredpixel/shatteredpixeldungeon/Rankings",
            "com/shatteredpixel/shatteredpixeldungeon/SPDAction",
            "com/shatteredpixel/shatteredpixeldungeon/SPDSettings",
            "com/shatteredpixel/shatteredpixeldungeon/Statistics",
            "com/shatteredpixel/shatteredpixeldungeon/items/wands/Wand",
            "com/shatteredpixel/shatteredpixeldungeon/items/weapon/melee/MagesStaff"
    );

    private JacocoCoverageCsvExporter() {
    }

    /**
     * Coverage data for a single exec file.
     */
    public static class CoverageData {
        public int actionCounter;
        public long timestamp;
        public long relativeTimestamp;
        
        // Instructions
        public int coveredInstructions;
        public int totalInstructions;
        public double instructionCoverage;
        
        // Branches
        public int coveredBranches;
        public int totalBranches;
        public double branchCoverage;
        
        // Lines
        public int coveredLines;
        public int totalLines;
        public double lineCoverage;
        
        // Methods
        public int coveredMethods;
        public int totalMethods;
        public double methodCoverage;
        
        // Classes
        public int coveredClasses;
        public int totalClasses;
        public double classCoverage;
        
        // Complexity
        public int coveredComplexity;
        public int totalComplexity;
        public double complexityCoverage;

        public CoverageData(int actionCounter, long timestamp, long relativeTimestamp, IBundleCoverage bundle) {
            this.actionCounter = actionCounter;
            this.timestamp = timestamp;
            this.relativeTimestamp = relativeTimestamp;
            
            // Extract coverage from bundle
            extractCoverage(bundle);
        }

        private void extractCoverage(IBundleCoverage bundle) {
            // Instructions
            ICounter instrCounter = bundle.getInstructionCounter();
            this.coveredInstructions = instrCounter.getCoveredCount();
            this.totalInstructions = instrCounter.getTotalCount();
            this.instructionCoverage = calculatePercentage(coveredInstructions, totalInstructions);
            
            // Branches
            ICounter branchCounter = bundle.getBranchCounter();
            this.coveredBranches = branchCounter.getCoveredCount();
            this.totalBranches = branchCounter.getTotalCount();
            this.branchCoverage = calculatePercentage(coveredBranches, totalBranches);
            
            // Lines
            ICounter lineCounter = bundle.getLineCounter();
            this.coveredLines = lineCounter.getCoveredCount();
            this.totalLines = lineCounter.getTotalCount();
            this.lineCoverage = calculatePercentage(coveredLines, totalLines);
            
            // Methods
            ICounter methodCounter = bundle.getMethodCounter();
            this.coveredMethods = methodCounter.getCoveredCount();
            this.totalMethods = methodCounter.getTotalCount();
            this.methodCoverage = calculatePercentage(coveredMethods, totalMethods);
            
            // Classes
            ICounter classCounter = bundle.getClassCounter();
            this.coveredClasses = classCounter.getCoveredCount();
            this.totalClasses = classCounter.getTotalCount();
            this.classCoverage = calculatePercentage(coveredClasses, totalClasses);
            
            // Complexity
            ICounter complexityCounter = bundle.getComplexityCounter();
            this.coveredComplexity = complexityCounter.getCoveredCount();
            this.totalComplexity = complexityCounter.getTotalCount();
            this.complexityCoverage = calculatePercentage(coveredComplexity, totalComplexity);
        }

        private double calculatePercentage(int covered, int total) {
            if (total == 0) return 0.0;
            return (100.0 * covered) / total;
        }

        /**
         * Converts this coverage data to a CSV row.
         */
        public String toCsvRow() {
            return String.format("%d,%d,%d," +
                    "%d,%d,%.4f," +
                    "%d,%d,%.4f," +
                    "%d,%d,%.4f," +
                    "%d,%d,%.4f," +
                    "%d,%d,%.4f," +
                    "%d,%d,%.4f",
                    actionCounter, timestamp, relativeTimestamp,
                    coveredInstructions, totalInstructions, instructionCoverage,
                    coveredBranches, totalBranches, branchCoverage,
                    coveredLines, totalLines, lineCoverage,
                    coveredMethods, totalMethods, methodCoverage,
                    coveredClasses, totalClasses, classCoverage,
                    coveredComplexity, totalComplexity, complexityCoverage);
        }

        /**
         * Returns the CSV header.
         */
        public static String getCsvHeader() {
            return "actionCounter,timestamp,relativeTimestamp," +
                    "coveredInstructions,totalInstructions,instructionCoverage," +
                    "coveredBranches,totalBranches,branchCoverage," +
                    "coveredLines,totalLines,lineCoverage," +
                    "coveredMethods,totalMethods,methodCoverage," +
                    "coveredClasses,totalClasses,classCoverage," +
                    "coveredComplexity,totalComplexity,complexityCoverage";
        }
    }

    /**
     * Exports coverage data from all exec files to CSV.
     *
     * @throws IOException if an I/O error occurs
     */
    public static void exportAllToCsv() throws IOException {
        exportToCsv(new File(DEFAULT_EXEC_DIR), new File(DEFAULT_CSV_OUTPUT_PATH), 
                   new File(DEFAULT_CLASSES_DIR), new File(DEFAULT_JSONL_DIR));
    }

    /**
     * Exports coverage data from exec files to CSV with custom paths.
     *
     * @param execDir directory containing .exec files
     * @param csvOutputFile output CSV file
     * @param classesDir directory containing compiled classes
     * @param jsonlDir directory containing action JSONL files
     * @throws IOException if an I/O error occurs
     */
    public static void exportToCsv(File execDir, File csvOutputFile, File classesDir, File jsonlDir) throws IOException {
        if (!execDir.exists() || !execDir.isDirectory()) {
            throw new IllegalArgumentException("Exec directory does not exist: " + execDir);
        }

        if (!classesDir.exists() || !classesDir.isDirectory()) {
            throw new IllegalArgumentException("Classes directory does not exist: " + classesDir);
        }

        // Create output directory if needed
        File outputDir = csvOutputFile.getParentFile();
        if (outputDir != null && !outputDir.exists() && !outputDir.mkdirs()) {
            throw new IOException("Failed to create output directory: " + outputDir);
        }

        // Find all cumulative exec files
        List<File> execFiles = findCumulativeExecFiles(execDir);
        if (execFiles.isEmpty()) {
            System.out.println("No exec files found in " + execDir);
            return;
        }

        // Load action counter mapping from JSONL files
        Map<Long, Integer> timestampToActionCounter = loadActionCounterMapping(jsonlDir);

        // Collect all coverage data
        List<CoverageData> coverageDataList = new ArrayList<>();
        long minTimestamp = Long.MAX_VALUE;

        System.out.println("Processing " + execFiles.size() + " exec files...\n");

        int fileNumber = 0;
        for (File execFile : execFiles) {
            fileNumber++;
            System.out.print("\rProcessing file " + fileNumber + "/" + execFiles.size() + ": " + execFile.getName() + "...");
            
            try {
                // Extract timestamp from filename
                long timestamp = extractTimestampFromFilename(execFile.getName());
                
                // Track minimum timestamp for relative calculation
                if (timestamp < minTimestamp) {
                    minTimestamp = timestamp;
                }

                // Get action counter (default to -1 if not found)
                int actionCounter = timestampToActionCounter.getOrDefault(timestamp, -1);

                // Analyze exec file and get coverage
                IBundleCoverage bundle = analyzeCoverage(execFile, classesDir);

                // Create coverage data
                CoverageData data = new CoverageData(actionCounter, timestamp, 0, bundle);
                coverageDataList.add(data);
                
                System.out.print(" ✓");

            } catch (Exception e) {
                System.err.println("\nFailed to process " + execFile.getName() + ": " + e.getMessage());
            }
        }
        
        System.out.println("\n"); // New line after progress

        // Calculate relative timestamps
        for (CoverageData data : coverageDataList) {
            data.relativeTimestamp = data.timestamp - minTimestamp;
        }

        // Sort by timestamp
        coverageDataList.sort(Comparator.comparingLong(d -> d.timestamp));

        // Write to CSV
        writeCsv(csvOutputFile, coverageDataList);

        System.out.println("Coverage data exported to: " + csvOutputFile.getAbsolutePath());
        System.out.println("Total entries: " + coverageDataList.size());
    }

    /**
     * Exports coverage data with interval jump.
     *
     * @param intervalJump process every Nth file
     * @throws IOException if an I/O error occurs
     */
    public static void exportToCsv(int intervalJump) throws IOException {
        File execDir = new File(DEFAULT_EXEC_DIR);
        File csvOutputFile = new File(DEFAULT_CSV_OUTPUT_PATH);
        File classesDir = new File(DEFAULT_CLASSES_DIR);
        File jsonlDir = new File(DEFAULT_JSONL_DIR);

        if (!execDir.exists() || !execDir.isDirectory()) {
            throw new IllegalArgumentException("Exec directory does not exist: " + execDir);
        }

        if (!classesDir.exists() || !classesDir.isDirectory()) {
            throw new IllegalArgumentException("Classes directory does not exist: " + classesDir);
        }

        // Create output directory if needed
        File outputDir = csvOutputFile.getParentFile();
        if (outputDir != null && !outputDir.exists() && !outputDir.mkdirs()) {
            throw new IOException("Failed to create output directory: " + outputDir);
        }

        // Find all cumulative exec files
        List<File> execFiles = findCumulativeExecFiles(execDir);
        if (execFiles.isEmpty()) {
            System.out.println("No exec files found in " + execDir);
            return;
        }

        // Load action counter mapping
        Map<Long, Integer> timestampToActionCounter = loadActionCounterMapping(jsonlDir);

        // Collect coverage data with interval jump
        List<CoverageData> coverageDataList = new ArrayList<>();
        long minTimestamp = Long.MAX_VALUE;

        int totalToProcess = (execFiles.size() + intervalJump - 1) / intervalJump; // Ceiling division
        System.out.println("Processing every " + intervalJump + " file(s) from " + execFiles.size() + " total files...");
        System.out.println("Will process approximately " + totalToProcess + " files.\n");

        int processedCount = 0;
        for (int i = 0; i < execFiles.size(); i += intervalJump) {
            File execFile = execFiles.get(i);
            processedCount++;
            System.out.print("\rProcessing file " + processedCount + "/" + totalToProcess + " (file #" + (i + 1) + "): " + execFile.getName() + "...");
            
            try {
                long timestamp = extractTimestampFromFilename(execFile.getName());
                if (timestamp < minTimestamp) {
                    minTimestamp = timestamp;
                }

                int actionCounter = timestampToActionCounter.getOrDefault(timestamp, -1);
                IBundleCoverage bundle = analyzeCoverage(execFile, classesDir);
                CoverageData data = new CoverageData(actionCounter, timestamp, 0, bundle);
                coverageDataList.add(data);
                
                System.out.print(" ✓");

            } catch (Exception e) {
                System.err.println("\nFailed to process " + execFile.getName() + ": " + e.getMessage());
            }
        }
        
        System.out.println("\n"); // New line after progress

        // Calculate relative timestamps
        for (CoverageData data : coverageDataList) {
            data.relativeTimestamp = data.timestamp - minTimestamp;
        }

        // Sort by timestamp
        coverageDataList.sort(Comparator.comparingLong(d -> d.timestamp));

        // Write to CSV
        writeCsv(csvOutputFile, coverageDataList);

        System.out.println("Coverage data exported to: " + csvOutputFile.getAbsolutePath());
        System.out.println("Total entries: " + coverageDataList.size());
    }

    /**
     * Analyzes a single exec file and returns coverage data.
     */
    private static IBundleCoverage analyzeCoverage(File execFile, File classesDir) throws IOException {
        // Load execution data
        ExecFileLoader execFileLoader = new ExecFileLoader();
        try (FileInputStream fis = new FileInputStream(execFile)) {
            execFileLoader.load(fis);
        }

        ExecutionDataStore executionDataStore = execFileLoader.getExecutionDataStore();
        CoverageBuilder coverageBuilder = new CoverageBuilder();

        // Analyze with exclusions
        Analyzer analyzer = new Analyzer(executionDataStore, coverageBuilder);
        analyzeWithExclusions(analyzer, classesDir, "", EXCLUDED_PACKAGES, EXCLUDED_CLASSES);

        // Return bundle
        return coverageBuilder.getBundle(AGENT_NAME);
    }

    /**
     * Recursively analyzes class files with exclusion filter.
     */
    private static void analyzeWithExclusions(Analyzer analyzer, File dir, String packagePath,
                                              List<String> excludedPackages,
                                              List<String> excludedClasses) throws IOException {
        File[] files = dir.listFiles();
        if (files == null) {
            return;
        }

        for (File file : files) {
            String currentPath = packagePath.isEmpty() ? file.getName() : packagePath + "/" + file.getName();

            if (file.isDirectory()) {
                String dirPath = currentPath + "/";
                if (!isExcluded(dirPath, excludedPackages)) {
                    analyzeWithExclusions(analyzer, file, currentPath, excludedPackages, excludedClasses);
                }
            } else if (file.getName().endsWith(".class")) {
                String classPath = currentPath.replace(".class", "");
                if (!isExcluded(classPath, excludedClasses)) {
                    analyzer.analyzeAll(file);
                }
            }
        }
    }

    /**
     * Checks if a path is excluded.
     */
    private static boolean isExcluded(String path, List<String> exclusions) {
        for (String exclusion : exclusions) {
            if (path.startsWith(exclusion)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Finds cumulative exec files sorted by modification time.
     */
    private static List<File> findCumulativeExecFiles(File execDir) {
        File[] files = execDir.listFiles((dir, name) ->
                name.endsWith(".exec") && !name.contains("_delta.exec")
        );

        if (files == null || files.length == 0) {
            return Collections.emptyList();
        }

        List<File> fileList = Arrays.asList(files);
        fileList.sort(Comparator.comparingLong(File::lastModified));
        return fileList;
    }

    /**
     * Extracts timestamp from exec filename.
     * Expected format: agentName_yy_MM_dd_timestamp.exec
     */
    private static long extractTimestampFromFilename(String filename) {
        Pattern pattern = Pattern.compile("_(\\d+)\\.exec$");
        Matcher matcher = pattern.matcher(filename);
        if (matcher.find()) {
            return Long.parseLong(matcher.group(1));
        }
        return 0;
    }

    /**
     * Loads action counter mapping from JSONL files.
     * Returns a map of timestamp -> actionCounter.
     */
    private static Map<Long, Integer> loadActionCounterMapping(File jsonlDir) {
        Map<Long, Integer> mapping = new HashMap<>();

        if (!jsonlDir.exists() || !jsonlDir.isDirectory()) {
            System.out.println("JSONL directory not found: " + jsonlDir);
            return mapping;
        }

        File[] jsonlFiles = jsonlDir.listFiles((dir, name) -> name.endsWith(".jsonl"));
        if (jsonlFiles == null || jsonlFiles.length == 0) {
            System.out.println("No JSONL files found in: " + jsonlDir);
            return mapping;
        }

        for (File jsonlFile : jsonlFiles) {
            try (BufferedReader reader = new BufferedReader(new FileReader(jsonlFile))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    // Simple JSON parsing (assumes format: {"actionCounter":X,"action":"...","env":"...","currenttimestamp":Y})
                    int actionCounter = extractJsonInt(line, "actionCounter");
                    long timestamp = extractJsonLong(line, "currenttimestamp");
                    if (actionCounter >= 0 && timestamp > 0) {
                        mapping.put(timestamp, actionCounter);
                    }
                }
            } catch (IOException e) {
                System.err.println("Failed to read JSONL file: " + jsonlFile.getName());
            }
        }

        System.out.println("Loaded " + mapping.size() + " action counter mappings from JSONL");
        return mapping;
    }

    /**
     * Simple JSON integer extraction.
     */
    private static int extractJsonInt(String json, String key) {
        Pattern pattern = Pattern.compile("\"" + key + "\":(\\d+)");
        Matcher matcher = pattern.matcher(json);
        if (matcher.find()) {
            return Integer.parseInt(matcher.group(1));
        }
        return -1;
    }

    /**
     * Simple JSON long extraction.
     */
    private static long extractJsonLong(String json, String key) {
        Pattern pattern = Pattern.compile("\"" + key + "\":(\\d+)");
        Matcher matcher = pattern.matcher(json);
        if (matcher.find()) {
            return Long.parseLong(matcher.group(1));
        }
        return -1;
    }

    /**
     * Writes coverage data to CSV file.
     */
    private static void writeCsv(File csvFile, List<CoverageData> dataList) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(csvFile))) {
            // Write header
            writer.write(CoverageData.getCsvHeader());
            writer.newLine();

            // Write data rows
            for (CoverageData data : dataList) {
                writer.write(data.toCsvRow());
                writer.newLine();
            }
        }
    }

    /**
     * Main method for standalone execution.
     */
    public static void main(String[] args) {
        try {
            int intervalJump = 1;
            if (args.length > 0) {
                intervalJump = Integer.parseInt(args[0]);
            }

            System.out.println("=== JaCoCo Coverage CSV Exporter ===");
            System.out.println("Agent Name: " + AGENT_NAME);
            System.out.println("Exec Directory: " + DEFAULT_EXEC_DIR);
            System.out.println("CSV Output: " + DEFAULT_CSV_OUTPUT_PATH);
            System.out.println("Classes Directory: " + DEFAULT_CLASSES_DIR);
            System.out.println("JSONL Directory: " + DEFAULT_JSONL_DIR);
            System.out.println("Interval Jump: " + intervalJump);
            System.out.println("====================================\n");

            if (intervalJump == 1) {
                exportAllToCsv();
            } else {
                exportToCsv(intervalJump);
            }

            System.out.println("\n=== Export Complete ===");
            System.out.println("CSV file contains coverage data with exclusions applied.");
            System.out.println("Columns: actionCounter, timestamp, relativeTimestamp, and all coverage categories.");

        } catch (Exception e) {
            System.err.println("Error exporting coverage to CSV: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}

