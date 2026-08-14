#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const CATEGORIES_DIR = path.join(process.cwd(), 'categories');
const SCRIPTS_JSON = path.join(process.cwd(), 'scripts.json');

/**
 * Parse JSDoc/comments from script to extract metadata
 */
function extractMetadata(content, filePath) {
  const filename = path.basename(filePath, path.extname(filePath));
  const category = path.basename(path.dirname(filePath));
  
  // Extract JSDoc or first comment block
  const jsdocMatch = content.match(/\/\*\*[\s\S]*?\*\//);
  const commentMatch = content.match(/\/\/\s*(.+)/);
  
  let description = '';
  let tags = [];
  let name = filename.replace(/-/g, ' ').replace(/^\w/, c => c.toUpperCase());

  if (jsdocMatch) {
    const jsdoc = jsdocMatch[0];
    
    // Extract @description or first text
    const descMatch = jsdoc.match(/@description\s+(.+?)(?=@|\*\/)/);
    description = descMatch ? descMatch[1].trim() : jsdoc.match(/\*\s+(.+)/)?.[1] || '';
    
    // Extract @name
    const nameMatch = jsdoc.match(/@name\s+(.+?)(?=@|\*\/)/);
    if (nameMatch) name = nameMatch[1].trim();
    
    // Extract @tags
    const tagsMatch = jsdoc.match(/@tags?\s+(.+?)(?=@|\*\/)/);
    if (tagsMatch) tags = tagsMatch[1].split(',').map(t => t.trim()).filter(Boolean);
  } else if (commentMatch) {
    description = commentMatch[1];
  }

  return {
    id: filename,
    name: name,
    category: category,
    file: path.relative(process.cwd(), filePath),
    description: description || 'No description provided',
    tags: tags.length > 0 ? tags : [category],
    updated: new Date().toISOString().split('T')[0],
    hash: crypto.createHash('md5').update(content).digest('hex')
  };
}

/**
 * Recursively find all scripts in categories/
 */
function findScripts(dir, extensions = ['.js', '.ts', '.py']) {
  const scripts = [];
  
  if (!fs.existsSync(dir)) return scripts;

  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      scripts.push(...findScripts(fullPath, extensions));
    } else if (extensions.includes(path.extname(entry.name))) {
      scripts.push(fullPath);
    }
  }
  
  return scripts;
}

/**
 * Load or create scripts.json
 */
function loadScriptsJson() {
  if (fs.existsSync(SCRIPTS_JSON)) {
    return JSON.parse(fs.readFileSync(SCRIPTS_JSON, 'utf8'));
  }
  return { scripts: [], lastUpdated: new Date().toISOString() };
}

/**
 * Main indexing function
 */
function indexScripts() {
  const scriptPaths = findScripts(CATEGORIES_DIR);
  const existing = loadScriptsJson();
  
  // Create a map of existing scripts by file path for quick lookup
  const existingMap = new Map(existing.scripts.map(s => [s.file, s]));
  
  const updated = [];
  const newScripts = [];

  for (const scriptPath of scriptPaths) {
    const content = fs.readFileSync(scriptPath, 'utf8');
    const metadata = extractMetadata(content, scriptPath);
    const relativePath = metadata.file;

    if (existingMap.has(relativePath)) {
      const existing = existingMap.get(relativePath);
      // Only update if content hash changed
      if (existing.hash !== metadata.hash) {
        console.log(`✓ Updated: ${relativePath}`);
        updated.push(metadata);
      } else {
        // Keep existing entry unchanged
        updated.push(existing);
      }
    } else {
      console.log(`✨ New: ${relativePath}`);
      newScripts.push(metadata);
      updated.push(metadata);
    }
  }

  // Remove scripts whose files no longer exist
  for (const script of existing.scripts) {
    if (!scriptPaths.some(p => path.relative(process.cwd(), p) === script.file)) {
      console.log(`✗ Removed: ${script.file}`);
    }
  }

  // Sort by category, then name
  updated.sort((a, b) => {
    if (a.category !== b.category) return a.category.localeCompare(b.category);
    return a.name.localeCompare(b.name);
  });

  const output = {
    scripts: updated,
    lastUpdated: new Date().toISOString(),
    stats: {
      total: updated.length,
      new: newScripts.length,
      updated: updated.length - newScripts.length
    }
  };

  fs.writeFileSync(SCRIPTS_JSON, JSON.stringify(output, null, 2) + '\n');
  console.log(`\n📝 scripts.json updated: ${updated.length} scripts indexed`);
}

try {
  indexScripts();
} catch (error) {
  console.error('Error indexing scripts:', error);
  process.exit(1);
}
