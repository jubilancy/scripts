/**
 * @name String Utilities
 * @description Common string manipulation functions (camelCase, snake_case, capitalize)
 * @tags string, utilities, text, formatting
 */

function toCamelCase(str) {
  return str.replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => {
    return index === 0 ? word.toLowerCase() : word.toUpperCase();
  }).replace(/\s+/g, '');
}

function toSnakeCase(str) {
  return str.replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s\-]+/g, '_')
    .toLowerCase();
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function reverseString(str) {
  return str.split('').reverse().join('');
}

function isPalindrome(str) {
  const cleaned = str.toLowerCase().replace(/\s/g, '');
  return cleaned === reverseString(cleaned);
}

// Usage:
// toCamelCase("hello world") → "helloWorld"
// toSnakeCase("helloWorld") → "hello_world"
// capitalize("javascript") → "Javascript"
// isPalindrome("racecar") → true
