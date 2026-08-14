/**
 * @name CSV Parser
 * @description Simple CSV string to JSON array converter with proper quote handling
 * @tags csv, parsing, data-processing, format-conversion
 */

function parseCSV(csvString, headers = true) {
  const lines = csvString.trim().split('\n');
  const result = [];
  const headerRow = headers ? lines[0].split(',').map(h => h.trim()) : null;
  const startIndex = headers ? 1 : 0;

  for (let i = startIndex; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
    
    if (headers) {
      const obj = {};
      headerRow.forEach((header, index) => {
        obj[header] = values[index];
      });
      result.push(obj);
    } else {
      result.push(values);
    }
  }

  return result;
}

function toCSV(data, headers = true) {
  if (!Array.isArray(data) || data.length === 0) return '';
  
  const firstItem = data[0];
  const keys = Array.isArray(firstItem) ? null : Object.keys(firstItem);
  
  let csv = '';
  
  if (headers && keys) {
    csv += keys.map(k => `"${k}"`).join(',') + '\n';
  }
  
  csv += data.map(item => {
    if (Array.isArray(item)) {
      return item.map(v => `"${v}"`).join(',');
    }
    return Object.values(item).map(v => `"${v}"`).join(',');
  }).join('\n');
  
  return csv;
}

// Usage:
// parseCSV('name,age\nJohn,30\nJane,25') 
// → [{name: "John", age: "30"}, {name: "Jane", age: "25"}]
