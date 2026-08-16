package com.shatteredpixel.shatteredpixeldungeon.agent.jacocoReporter;

import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.IBundleCoverage;
import org.jacoco.core.data.ExecutionDataStore;
import org.jacoco.core.tools.ExecFileLoader;
import org.jacoco.report.IReportVisitor;
import org.jacoco.report.xml.XMLFormatter;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

/**
 * Utility class for generating XML reports from JaCoCo exec files.
 * Supports batch generation with configurable exclusions and intervals.
 */
public final class JacocoXmlReportGenerator {

    private static final String AGENT_NAME = "agentAggression1";

    // Exclusion packages - classes under these packages will be excluded
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

    // Exclusion classes - specific classes to exclude
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

    // Default paths
    private static final String DEFAULT_EXEC_DIR = "../out/SPD/jacoco-reports/" + AGENT_NAME;
    private static final String DEFAULT_XML_OUTPUT_DIR = "../out/SPD/jacoco-xml-reports/" + AGENT_NAME;
    private static final String DEFAULT_CLASSES_DIR = "./core/build/classes/java/main";

    // Configurable paths from environment
    private static final String EXEC_DIR = DEFAULT_EXEC_DIR;
    private static final String XML_OUTPUT_DIR = DEFAULT_XML_OUTPUT_DIR;
    private static final String CLASSES_DIR = DEFAULT_CLASSES_DIR;

    private JacocoXmlReportGenerator() {
    }

    /**
     * Configuration for XML report generation.
     */
    public static class ReportConfig {
        public final File execDir;
        public final File xmlOutputDir;
        public final File classesDir;
        public final int intervalJump;
        public final List<String> excludedPackages;
        public final List<String> excludedClasses;

        public ReportConfig(File execDir, File xmlOutputDir, File classesDir, int intervalJump,
                            List<String> excludedPackages, List<String> excludedClasses) {
            this.execDir = execDir;
            this.xmlOutputDir = xmlOutputDir;
            this.classesDir = classesDir;
            this.intervalJump = intervalJump;
            this.excludedPackages = excludedPackages != null ? excludedPackages : EXCLUDED_PACKAGES;
            this.excludedClasses = excludedClasses != null ? excludedClasses : EXCLUDED_CLASSES;
        }
    }

    /**
     * Builder for ReportConfig with default values.
     */
    public static class ReportConfigBuilder {
        private File execDir = new File(EXEC_DIR);
        private File xmlOutputDir = new File(XML_OUTPUT_DIR);
        private File classesDir = new File(CLASSES_DIR);
        private int intervalJump = 1;
        private List<String> excludedPackages = EXCLUDED_PACKAGES;
        private List<String> excludedClasses = EXCLUDED_CLASSES;

        public ReportConfigBuilder execDir(File execDir) {
            this.execDir = execDir;
            return this;
        }

        public ReportConfigBuilder execDir(String execDir) {
            this.execDir = new File(execDir);
            return this;
        }

        public ReportConfigBuilder xmlOutputDir(File xmlOutputDir) {
            this.xmlOutputDir = xmlOutputDir;
            return this;
        }

        public ReportConfigBuilder xmlOutputDir(String xmlOutputDir) {
            this.xmlOutputDir = new File(xmlOutputDir);
            return this;
        }

        public ReportConfigBuilder classesDir(File classesDir) {
            this.classesDir = classesDir;
            return this;
        }

        public ReportConfigBuilder classesDir(String classesDir) {
            this.classesDir = new File(classesDir);
            return this;
        }

        public ReportConfigBuilder intervalJump(int intervalJump) {
            this.intervalJump = intervalJump;
            return this;
        }

        public ReportConfigBuilder excludedPackages(List<String> excludedPackages) {
            this.excludedPackages = excludedPackages;
            return this;
        }

        public ReportConfigBuilder excludedClasses(List<String> excludedClasses) {
            this.excludedClasses = excludedClasses;
            return this;
        }

        public ReportConfigBuilder addExcludedPackage(String packageName) {
            if (this.excludedPackages == EXCLUDED_PACKAGES) {
                this.excludedPackages = new ArrayList<>(EXCLUDED_PACKAGES);
            }
            this.excludedPackages.add(packageName);
            return this;
        }

        public ReportConfigBuilder addExcludedClass(String className) {
            if (this.excludedClasses == EXCLUDED_CLASSES) {
                this.excludedClasses = new ArrayList<>(EXCLUDED_CLASSES);
            }
            this.excludedClasses.add(className);
            return this;
        }

        public ReportConfig build() {
            return new ReportConfig(execDir, xmlOutputDir, classesDir, intervalJump,
                    excludedPackages, excludedClasses);
        }
    }

    /**
     * Generates XML reports for all exec files in the configured directory.
     * Uses default configuration with interval jump of 1 (every file).
     *
     * @throws IOException if an I/O error occurs
     */
    public static void generateAllReports() throws IOException {
        generateReports(new ReportConfigBuilder().build());
    }

    /**
     * Generates XML reports for exec files with the specified interval jump.
     *
     * @param intervalJump generate report every N-th file (1 = every file, 2 = every other file, etc.)
     * @throws IOException if an I/O error occurs
     */
    public static void generateReports(int intervalJump) throws IOException {
        generateReports(new ReportConfigBuilder().intervalJump(intervalJump).build());
    }

    /**
     * Generates XML reports for exec files in the given directory.
     *
     * @param execDir directory containing .exec files
     * @throws IOException if an I/O error occurs
     */
    public static void generateReports(File execDir) throws IOException {
        generateReports(new ReportConfigBuilder().execDir(execDir).build());
    }

    /**
     * Generates XML reports for exec files based on the provided configuration.
     *
     * @param config configuration for report generation
     * @throws IOException if an I/O error occurs
     */
    public static void generateReports(ReportConfig config) throws IOException {
        if (!config.execDir.exists() || !config.execDir.isDirectory()) {
            throw new IllegalArgumentException("Exec directory does not exist: " + config.execDir);
        }

        if (!config.classesDir.exists() || !config.classesDir.isDirectory()) {
            throw new IllegalArgumentException("Classes directory does not exist: " + config.classesDir);
        }

        // Create output directory if it doesn't exist
        if (!config.xmlOutputDir.exists() && !config.xmlOutputDir.mkdirs()) {
            throw new IOException("Failed to create XML output directory: " + config.xmlOutputDir);
        }

        // Find all cumulative exec files (excluding delta files)
        List<File> execFiles = findCumulativeExecFiles(config.execDir);

        if (execFiles.isEmpty()) {
            System.out.println("No exec files found in " + config.execDir);
            return;
        }

        System.out.println("Found " + execFiles.size() + " exec files");
        System.out.println("Generating XML reports with interval jump: " + config.intervalJump);

        int reportCount = 0;
        for (int i = 0; i < execFiles.size(); i += config.intervalJump) {
            File execFile = execFiles.get(i);
            try {
                String xmlFileName = execFile.getName().replace(".exec", ".xml");
                File xmlFile = new File(config.xmlOutputDir, xmlFileName);

                generateSingleReport(execFile, xmlFile, config);
                reportCount++;

                System.out.println("Generated report " + reportCount + ": " + xmlFile.getName());
            } catch (Exception e) {
                System.err.println("Failed to generate report for " + execFile.getName() + ": " + e.getMessage());
                e.printStackTrace();
            }
        }

        System.out.println("XML report generation completed. Generated " + reportCount + " reports.");
    }

    /**
     * Generates a single XML report from an exec file with exclusions.
     * 
     * IMPORTANT: Exclusions are applied DURING the analysis phase, which means:
     * 1. Excluded classes/packages are NEVER analyzed
     * 2. They do NOT appear in the CoverageBuilder
     * 3. They are NOT included in the XML report
     * 4. Total coverage calculations from the XML will AUTOMATICALLY exclude them
     * 
     * This ensures that when you fetch total coverage from the XML report later,
     * the totals will NOT include any data from excluded packages/classes.
     *
     * @param execFile  input .exec file
     * @param xmlFile   output .xml file
     * @param config    configuration with exclusions
     * @throws IOException if an I/O error occurs
     */
    public static void generateSingleReport(File execFile, File xmlFile, ReportConfig config) throws IOException {
        // Load execution data from .exec file
        ExecFileLoader execFileLoader = new ExecFileLoader();
        try (FileInputStream fis = new FileInputStream(execFile)) {
            execFileLoader.load(fis);
        }

        ExecutionDataStore executionDataStore = execFileLoader.getExecutionDataStore();

        // Create coverage builder (will only contain NON-EXCLUDED classes)
        CoverageBuilder coverageBuilder = new CoverageBuilder();

        // Analyze classes with exclusion filter applied
        // CRITICAL: Only non-excluded classes are analyzed here
        // This means excluded classes NEVER enter the coverage data
        Analyzer analyzer = new Analyzer(executionDataStore, coverageBuilder);
        analyzeWithExclusions(analyzer, config.classesDir, config.excludedPackages, config.excludedClasses);

        // Create bundle from analyzed classes only (excludes filtered classes)
        // The bundle's total coverage will NOT include excluded packages/classes
        IBundleCoverage bundle = coverageBuilder.getBundle(AGENT_NAME);

        // Generate XML report from the filtered bundle
        // Total coverage in XML = coverage of NON-EXCLUDED classes only
        XMLFormatter xmlFormatter = new XMLFormatter();
        try (FileOutputStream fos = new FileOutputStream(xmlFile)) {
            IReportVisitor visitor = xmlFormatter.createVisitor(fos);
            visitor.visitInfo(execFileLoader.getSessionInfoStore().getInfos(),
                    execFileLoader.getExecutionDataStore().getContents());
            visitor.visitBundle(bundle, null);
            visitor.visitEnd();
        }
    }

    /**
     * Analyzes class files with exclusions.
     * Only non-excluded classes will be added to the coverage builder.
     */
    private static void analyzeWithExclusions(Analyzer analyzer, File classesDir,
                                              List<String> excludedPackages,
                                              List<String> excludedClasses) throws IOException {
        analyzeDirectory(analyzer, classesDir, "", excludedPackages, excludedClasses);
    }

    /**
     * Prints a summary of what will be included/excluded in the coverage analysis.
     * Useful for verifying that exclusions are properly configured.
     */
    public static void printExclusionSummary() {
        System.out.println("\n=== JaCoCo XML Report Generator - Exclusion Summary ===");
        System.out.println("\nEXCLUDED PACKAGES (" + EXCLUDED_PACKAGES.size() + "):");
        for (String pkg : EXCLUDED_PACKAGES) {
            System.out.println("  - " + pkg);
        }
        System.out.println("\nEXCLUDED CLASSES (" + EXCLUDED_CLASSES.size() + "):");
        for (String cls : EXCLUDED_CLASSES) {
            System.out.println("  - " + cls);
        }
        System.out.println("\nIMPORTANT: These packages and classes will NOT be included in:");
        System.out.println("  - The coverage analysis");
        System.out.println("  - The generated XML reports");
        System.out.println("  - The total coverage calculations");
        System.out.println("\nWhen you fetch total coverage from XML reports, these exclusions");
        System.out.println("are AUTOMATICALLY applied - no post-processing needed!");
        System.out.println("=======================================================\n");
    }

    /**
     * Generates a single report and prints coverage statistics.
     * Useful for verifying that totals don't include excluded classes.
     */
    public static void generateSingleReportWithStats(File execFile, File xmlFile, ReportConfig config) throws IOException {
        System.out.println("\n--- Generating report for: " + execFile.getName() + " ---");
        System.out.println("Applying " + config.excludedPackages.size() + " package exclusions");
        System.out.println("Applying " + config.excludedClasses.size() + " class exclusions");
        
        // Load execution data
        ExecFileLoader execFileLoader = new ExecFileLoader();
        try (FileInputStream fis = new FileInputStream(execFile)) {
            execFileLoader.load(fis);
        }

        ExecutionDataStore executionDataStore = execFileLoader.getExecutionDataStore();
        CoverageBuilder coverageBuilder = new CoverageBuilder();

        // Analyze with exclusions
        Analyzer analyzer = new Analyzer(executionDataStore, coverageBuilder);
        analyzeWithExclusions(analyzer, config.classesDir, config.excludedPackages, config.excludedClasses);

        // Get bundle and print statistics
        IBundleCoverage bundle = coverageBuilder.getBundle(AGENT_NAME);
        
        System.out.println("\nCoverage Statistics (AFTER exclusions applied):");
        System.out.println("  Total Classes: " + bundle.getClassCounter().getTotalCount());
        System.out.println("  Covered Classes: " + bundle.getClassCounter().getCoveredCount());
        System.out.println("  Total Methods: " + bundle.getMethodCounter().getTotalCount());
        System.out.println("  Covered Methods: " + bundle.getMethodCounter().getCoveredCount());
        System.out.println("  Total Instructions: " + bundle.getInstructionCounter().getTotalCount());
        System.out.println("  Covered Instructions: " + bundle.getInstructionCounter().getCoveredCount());
        System.out.println("  Total Branches: " + bundle.getBranchCounter().getTotalCount());
        System.out.println("  Covered Branches: " + bundle.getBranchCounter().getCoveredCount());
        System.out.println("  Total Lines: " + bundle.getLineCounter().getTotalCount());
        System.out.println("  Covered Lines: " + bundle.getLineCounter().getCoveredCount());
        
        if (bundle.getInstructionCounter().getTotalCount() > 0) {
            double instructionCoverage = 100.0 * bundle.getInstructionCounter().getCoveredCount() 
                                        / bundle.getInstructionCounter().getTotalCount();
            System.out.println(String.format("  Instruction Coverage: %.4f%%", instructionCoverage));
        }
        
        // Generate XML report
        XMLFormatter xmlFormatter = new XMLFormatter();
        try (FileOutputStream fos = new FileOutputStream(xmlFile)) {
            IReportVisitor visitor = xmlFormatter.createVisitor(fos);
            visitor.visitInfo(execFileLoader.getSessionInfoStore().getInfos(),
                    execFileLoader.getExecutionDataStore().getContents());
            visitor.visitBundle(bundle, null);
            visitor.visitEnd();
        }
        
        System.out.println("\nXML report saved to: " + xmlFile.getAbsolutePath());
        System.out.println("NOTE: The above totals match what you'll see in the XML report.");
        System.out.println("Excluded classes/packages are NOT included in these totals.\n");
    }

    /**
     * Recursively analyzes class files in a directory, applying exclusion filters.
     */
    private static void analyzeDirectory(Analyzer analyzer, File dir, String packagePath,
                                         List<String> excludedPackages,
                                         List<String> excludedClasses) throws IOException {
        File[] files = dir.listFiles();
        if (files == null) {
            return;
        }

        for (File file : files) {
            String currentPath = packagePath.isEmpty() ? file.getName() : packagePath + "/" + file.getName();

            if (file.isDirectory()) {
                // Check if this package should be excluded
                String dirPath = currentPath + "/";
                if (isExcluded(dirPath, excludedPackages)) {
                    continue;
                }
                analyzeDirectory(analyzer, file, currentPath, excludedPackages, excludedClasses);
            } else if (file.getName().endsWith(".class")) {
                // Check if this class should be excluded
                String classPath = currentPath.replace(".class", "");
                if (isExcluded(classPath, excludedClasses)) {
                    continue;
                }
                analyzer.analyzeAll(file);
            }
        }
    }

    /**
     * Checks if a path matches any exclusion pattern.
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
     * Finds all cumulative exec files (excluding delta files) in the directory,
     * sorted by modification time.
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
     * Saves exclusion lists to separate files in the XML output directory.
     */
    public static void saveExclusionLists(File outputDir) throws IOException {
        if (!outputDir.exists() && !outputDir.mkdirs()) {
            throw new IOException("Failed to create output directory: " + outputDir);
        }

        // Save excluded packages
        File excludedPackagesFile = new File(outputDir, "excluded_packages.txt");
        try (FileOutputStream fos = new FileOutputStream(excludedPackagesFile)) {
            for (String pkg : EXCLUDED_PACKAGES) {
                fos.write((pkg + "\n").getBytes());
            }
        }

        // Save excluded classes
        File excludedClassesFile = new File(outputDir, "excluded_classes.txt");
        try (FileOutputStream fos = new FileOutputStream(excludedClassesFile)) {
            for (String cls : EXCLUDED_CLASSES) {
                fos.write((cls + "\n").getBytes());
            }
        }

        System.out.println("Exclusion lists saved to " + outputDir);
    }

    /**
     * Utility method to save default exclusion lists.
     */
    public static void saveExclusionLists() throws IOException {
        saveExclusionLists(new File(XML_OUTPUT_DIR));
    }

    /**
     * Main method for standalone execution.
     * Usage: java JacocoXmlReportGenerator [intervalJump]
     */
    public static void main(String[] args) {
        try {
            int intervalJump = 1;
            if (args.length > 0) {
                intervalJump = Integer.parseInt(args[0]);
            }

            System.out.println("=== JaCoCo XML Report Generator ===");
            System.out.println("Agent Name: " + AGENT_NAME);
            System.out.println("Exec Directory: " + EXEC_DIR);
            System.out.println("XML Output Directory: " + XML_OUTPUT_DIR);
            System.out.println("Classes Directory: " + CLASSES_DIR);
            System.out.println("Interval Jump: " + intervalJump);
            System.out.println("===================================");

            // Print exclusion summary
            printExclusionSummary();

            // Generate reports
            generateReports(intervalJump);

            // Save exclusion lists
            saveExclusionLists();

            System.out.println("\n=== Summary ===");
            System.out.println("All XML reports have been generated with exclusions applied.");
            System.out.println("When you fetch total coverage from these XML reports,");
            System.out.println("the totals will NOT include excluded packages/classes.");
            System.out.println("Exclusion lists saved to: " + XML_OUTPUT_DIR);
            System.out.println("Done!");

        } catch (Exception e) {
            System.err.println("Error generating XML reports: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}

