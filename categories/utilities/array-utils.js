/**
 * @name Array Utilities
 * @description Helper functions for array manipulation and operations
 * @tags array, utilities, data, operations
 */

function flatten(arr, depth = Infinity) {
  let level = 0;
  return arr.reduce((flat, item) => {
    return flat.concat(level < depth && Array.isArray(item) ? ((level++), flatten(item, depth), (level--)) : item);
  }, []);
}

function chunk(arr, size) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

function unique(arr) {
  return [...new Set(arr)];
}

function shuffle(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function groupBy(arr, key) {
  return arr.reduce((groups, item) => {
    const groupKey = typeof key === 'function' ? key(item) : item[key];
    if (!groups[groupKey]) groups[groupKey] = [];
    groups[groupKey].push(item);
    return groups;
  }, {});
}

// Usage:
// flatten([[1, 2], [3, [4, 5]]]) → [1, 2, 3, 4, 5]
// chunk([1, 2, 3, 4, 5], 2) → [[1, 2], [3, 4], [5]]
// unique([1, 2, 2, 3]) → [1, 2, 3]
// groupBy([{id: 1, type: 'a'}, {id: 2, type: 'a'}], 'type')
