// redux-persist's storage engine interface is just these three methods returning Promises.
// Written inline instead of `import storage from 'redux-persist/lib/storage'` because Vite 8's
// Rolldown-based dep optimizer has a CJS-interop bug on that subpath: the pre-bundled chunk does
// `export default require_storage()`, which exports the raw `{ __esModule, default }` CJS
// exports object instead of unwrapping `.default`, so `storage.getItem` is undefined at runtime.
const localStorageEngine = {
  getItem: (key) => Promise.resolve(window.localStorage.getItem(key)),
  setItem: (key, value) => Promise.resolve(window.localStorage.setItem(key, value)),
  removeItem: (key) => Promise.resolve(window.localStorage.removeItem(key)),
}

export default localStorageEngine
