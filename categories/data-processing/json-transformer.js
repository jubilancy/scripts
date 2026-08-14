/**
 * @name JSON Transformer
 * @description Flatten, nest, and transform nested JSON structures
 * @tags json, data-processing, transformation, nesting
 */

function flattenJSON(obj, prefix = '') {
  let result = {};
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const value = obj[key];
      const newKey = prefix ? `${prefix}.${key}` : key;
      
      if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
        Object.assign(result, flattenJSON(value, newKey));
      } else if (Array.isArray(value)) {
        result[newKey] = value;
      } else {
        result[newKey] = value;
      }
    }
  }
  
  return result;
}

function nestJSON(flatObj) {
  const result = {};
  
  for (const key in flatObj) {
    const parts = key.split('.');
    let current = result;
    
    for (let i = 0; i < parts.length - 1; i++) {
      if (!current[parts[i]]) {
        current[parts[i]] = {};
      }
      current = current[parts[i]];
    }
    
    current[parts[parts.length - 1]] = flatObj[key];
  }
  
  return result;
}

function transformJSON(obj, mapping) {
  const result = {};
  
  for (const [key, path] of Object.entries(mapping)) {
    const keys = path.split('.');
    let value = obj;
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    result[key] = value;
  }
  
  return result;
}

// Usage:
// flattenJSON({user: {name: "John", age: 30}})
// → {"user.name": "John", "user.age": 30}
