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
  --force             Replace existing .agent and AGENTS.md without creating backups.
  --no-agents-md      Install .agent only.
  --dry-run           Print planned actions without writing files.
  -h, --help          Show help.
  -v, --version       Show version.

Examples:
  npx github:KeithTorda/gravirules init
  npm install -g github:KeithTorda/gravirules
  ag-kit init
  npx @keithtorda/gravirules init
  npm install -g @keithtorda/gravirules
  ag-kit init
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

    if (arg === "--force") {
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

function timestamp() {
  const now = new Date();
  const pad = (value) => String(value).padStart(2, "0");
  return [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate()),
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds()),
  ].join("");
}

function backupPath(destination) {
  const parsed = path.parse(destination);
  const stamp = timestamp();
  const base = parsed.ext
    ? path.join(parsed.dir, `${parsed.name}.backup_${stamp}${parsed.ext}`)
    : `${destination}_backup_${stamp}`;

  if (!fs.existsSync(base)) {
    return base;
  }

  for (let index = 1; index < 100; index += 1) {
    const candidate = `${base}.${index}`;
    if (!fs.existsSync(candidate)) {
      return candidate;
    }
  }

  throw new Error(`Could not allocate backup path for ${destination}`);
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

  const backup = backupPath(destination);
  if (options.dryRun) {
    console.log(`[dry-run] backup ${destination} -> ${backup}`);
    return;
  }
  fs.renameSync(destination, backup);
  console.log(`Backed up ${path.basename(destination)} -> ${path.basename(backup)}`);
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
  prepareDestination(destinationAgent, options);
  copyRecursive(sourceAgent, destinationAgent, options);

  if (options.installAgentsMd) {
    const destinationAgentsMd = path.join(options.target, "AGENTS.md");
    prepareDestination(destinationAgentsMd, options);
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
