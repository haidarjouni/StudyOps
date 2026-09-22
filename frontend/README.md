# React + TypeScript + Tailwind CSS + Vite

This frontend uses React 19, TypeScript, Tailwind CSS 4, and Vite 8 with HMR and Oxlint.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## TypeScript and linting

TypeScript runs in strict mode, and the production build type-checks the application before Vite creates the bundle. Run `npm run lint` to check the source with Oxlint and `npm run build` to type-check and build the frontend.
