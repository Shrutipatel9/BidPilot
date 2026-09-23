import { combineReducers, configureStore } from '@reduxjs/toolkit'
import { FLUSH, PAUSE, PERSIST, PURGE, REGISTER, REHYDRATE, persistReducer, persistStore } from 'redux-persist'

import storage from './localStorageEngine'
import authReducer from '../features/auth/authSlice'
import { authApi } from '../features/auth/authApi'
import { orgApi } from '../features/org/orgApi'
import { projectApi } from '../features/project/projectApi'

// Only the auth slice persists (localStorage, via redux-persist) — RTK Query's own cache is
// deliberately not persisted, so server data is always fresh on load.
const persistedAuthReducer = persistReducer({ key: 'auth', storage }, authReducer)

const rootReducer = combineReducers({
  auth: persistedAuthReducer,
  [authApi.reducerPath]: authApi.reducer,
  [orgApi.reducerPath]: orgApi.reducer,
  [projectApi.reducerPath]: projectApi.reducer,
})

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // redux-persist dispatches non-serializable actions during rehydration — this is the
        // documented way to silence that specific, expected warning without disabling the
        // serializability check entirely.
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
        // createProject's mutation arg carries a raw File (questionnaire upload) — not
        // serializable by design, and not persisted, so it's safe to exclude from this check
        // specifically rather than disabling serializability checking more broadly.
        ignoredActionPaths: ['meta.arg.originalArgs.file'],
      },
    }).concat(authApi.middleware, orgApi.middleware, projectApi.middleware),
})

export const persistor = persistStore(store)
