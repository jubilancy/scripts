#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const CATEGORIES_DIR = path.join(process.cwd(), 'categories');
const CATEGORIES_JSON = path.join(process.cwd(), 'categories.json');

/**
 * Generate a description from folder name
 */
function generateDescription(folderName) {
  const words = folderName.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1));
  return words.join(' ');
}

/**
 * Generate emoji based on category name
 */
function getEmojiForCategory(name) {
  const emojiMap = {
    'web-tools': '🌐',
    'utilities': '🔧',
    'data-processing': '📊',
    'automation': '⚙️',
    'ui': '🎨',
    'api': '🔌',
    'database': '🗄️',
    'testing': '✅',
    'build': '🏗️',
    'deploy': '🚀',
    'security': '🔒',
    'monitoring': '📈',
    'analytics': '📉',
    'performance': '⚡',
    'parsing': '📄',
    'validation': '☑️',
    'formatting': '📝',
    'conversion': '🔄',
    'compression': '📦',
    'encryption': '🔐',
  };
  
  return emojiMap[name] || '📁';
}

/**
 * Scan categories folder and build category list
 */
function syncCategories() {
  if (!fs.existsSync(CATEGORIES_DIR)) {
    console.log('⚠️  categories/ folder not found');
    return;
  }

  const entries = fs.readdirSync(CATEGORIES_DIR, { withFileTypes: true });
  const categories = [];

  for (const entry of entries) {
    if (entry.isDirectory() && !entry.name.startsWith('.')) {
      const folderPath = path.join(CATEGORIES_DIR, entry.name);
      const scripts = fs.readdirSync(folderPath).filter(f => 
        /\.(js|ts|py|sh|rb|go|java|cpp|c)$/.test(f) && !f.startsWith('.')
      );

      const category = {
        id: entry.name,
        name: generateDescription(entry.name),
        slug: entry.name,
        description: `Collection of ${entry.name.replace(/-/g, ' ')} scripts`,
        emoji: getEmojiForCategory(entry.name),
        scriptCount: scripts.length,
        created: new Date().toISOString().split('T')[0],
        updated: new Date().toISOString().split('T')[0]
      };

      categories.push(category);
      console.log(`✓ Found category: ${entry.name} (${scripts.length} scripts)`);
    }
  }

  // Sort alphabetically
  categories.sort((a, b) => a.slug.localeCompare(b.slug));

  const output = {
    categories: categories,
    lastUpdated: new Date().toISOString(),
    stats: {
      total: categories.length
    }
  };

  fs.writeFileSync(CATEGORIES_JSON, JSON.stringify(output, null, 2) + '\n');
  console.log(`\n✨ categories.json generated: ${categories.length} categories indexed`);
}

try {
  syncCategories();
} catch (error) {
  console.error('Error syncing categories:', error);
  process.exit(1);
}
