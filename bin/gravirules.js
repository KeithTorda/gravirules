#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const VERSION = require(path.join(PACKAGE_ROOT, "package.json")).version;

function printHelp() {
  console.log(`GraviRules ${VERSION}

Usage:
  gravirules init [options]
  ag-kit init [options]

Options:
  --target <path>     Install into a specific project directory. Defaults to current directory.
  --force             Replace existing .agent and AGENTS.md.
  --fresh             Alias for --force. Use for clean reinstall.
  --no-agents-md      Install .agent only.
  --dry-run           Print planned actions without writing files.
  -h, --help          Show help.
  -v, --version       Show version.

Examples:
  npx github:KeithTorda/gravirules init
  npm install -g github:KeithTorda/gravirules
  ag-kit init --fresh
  npx @keithtorda/gravirules init --fresh
  npm install -g @keithtorda/gravirules
  ag-kit init --fresh
`);
}

function parseArgs(argv) {
  const options = {
    command: null,
    target: process.cwd(),
    force: false,
    installAgentsMd: true,
    dryRun: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (!options.command && !arg.startsWith("-")) {
      options.command = arg;
      continue;
    }

    if (arg === "--target") {
      const value = argv[index + 1];
      if (!value) {
        throw new Error("--target requires a path");
      }
      options.target = value;
      index += 1;
      continue;
    }

    if (arg === "--force" || arg === "--fresh") {
      options.force = true;
      continue;
    }

    if (arg === "--no-agents-md") {
      options.installAgentsMd = false;
      continue;
    }

    if (arg === "--dry-run") {
      options.dryRun = true;
      continue;
    }

    if (arg === "-h" || arg === "--help") {
      options.command = "help";
      continue;
    }

    if (arg === "-v" || arg === "--version") {
      options.command = "version";
      continue;
    }

    throw new Error(`Unknown option: ${arg}`);
  }

  options.command = options.command || "help";
  options.target = path.resolve(options.target);
  return options;
}

function ensureTargetDirectory(target, options) {
  if (!fs.existsSync(target)) {
    if (options.dryRun) {
      console.log(`[dry-run] create directory ${target}`);
      return;
    }
    fs.mkdirSync(target, { recursive: true });
    return;
  }

  const stat = fs.statSync(target);
  if (!stat.isDirectory()) {
    throw new Error(`Target is not a directory: ${target}`);
  }
}

function prepareDestination(destination, options) {
  if (!fs.existsSync(destination)) {
    return;
  }

  if (options.force) {
    if (options.dryRun) {
      console.log(`[dry-run] remove ${destination}`);
      return;
    }
    fs.rmSync(destination, { recursive: true, force: true });
    return;
  }

  const name = path.basename(destination);
  throw new Error(`${name} already exists. Use --fresh to replace it cleanly.`);
}

function isManagedAgent(destinationAgent) {
  const marker = path.join(destinationAgent, ".gravirules.json");
  if (fs.existsSync(marker)) {
    try {
      const data = JSON.parse(fs.readFileSync(marker, "utf8"));
      if (data.package === "@keithtorda/gravirules") {
        return true;
      }
    } catch (_) {
      return false;
    }
  }

  const indexPath = path.join(destinationAgent, "INDEX.md");
  const rulesPath = path.join(destinationAgent, "rules", "GEMINI.md");
  for (const candidate of [indexPath, rulesPath]) {
    if (fs.existsSync(candidate)) {
      const text = fs.readFileSync(candidate, "utf8");
      if (text.includes("GraviRules")) {
        return true;
      }
    }
  }

  return false;
}

function writeInstallMarker(destinationAgent, options) {
  const marker = path.join(destinationAgent, ".gravirules.json");
  const data = {
    package: "@keithtorda/gravirules",
    kit: "GraviRules",
    version: VERSION,
    installedAt: new Date().toISOString(),
  };

  if (options.dryRun) {
    console.log(`[dry-run] write ${marker}`);
    return;
  }

  fs.writeFileSync(marker, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function copyRecursive(source, destination, options) {
  const stat = fs.statSync(source);

  if (options.dryRun) {
    console.log(`[dry-run] copy ${source} -> ${destination}`);
    return;
  }

  if (stat.isDirectory()) {
    fs.mkdirSync(destination, { recursive: true });
    for (const entry of fs.readdirSync(source)) {
      if (entry === ".git" || entry === "node_modules" || entry === "__pycache__") {
        continue;
      }
      copyRecursive(path.join(source, entry), path.join(destination, entry), options);
    }
    return;
  }

  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
}

function installKit(options) {
  const sourceAgent = path.join(PACKAGE_ROOT, ".agent");
  const sourceAgentsMd = path.join(PACKAGE_ROOT, "AGENTS.md");

  if (!fs.existsSync(sourceAgent)) {
    throw new Error(`Package is missing .agent template: ${sourceAgent}`);
  }

  ensureTargetDirectory(options.target, options);

  const destinationAgent = path.join(options.target, ".agent");
  const managedAgent = fs.existsSync(destinationAgent) && isManagedAgent(destinationAgent);
  const replaceOptions = managedAgent ? { ...options, force: true } : options;
  if (managedAgent && !options.force && !options.dryRun) {
    console.log("Updating existing GraviRules .agent in place.");
  }

  prepareDestination(destinationAgent, replaceOptions);
  copyRecursive(sourceAgent, destinationAgent, options);
  writeInstallMarker(destinationAgent, options);

  if (options.installAgentsMd) {
    const destinationAgentsMd = path.join(options.target, "AGENTS.md");
    prepareDestination(destinationAgentsMd, replaceOptions);
    copyRecursive(sourceAgentsMd, destinationAgentsMd, options);
  }

  console.log("");
  console.log("GraviRules installed.");
  console.log(`Target: ${options.target}`);
  console.log("");
  console.log("Verify:");
  console.log("  python .agent/scripts/validate_agent_kit.py .");
  console.log("  python .agent/scripts/checklist.py .");
}

function main() {
  try {
    const options = parseArgs(process.argv.slice(2));

    if (options.command === "help") {
      printHelp();
      return;
    }

    if (options.command === "version") {
      console.log(VERSION);
      return;
    }

    if (options.command !== "init") {
      throw new Error(`Unknown command: ${options.command}`);
    }

    installKit(options);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    console.error("Run `gravirules --help` for usage.");
    process.exit(1);
  }
}

main();
