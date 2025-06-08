module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
    '../../**/!(node_modules)/**/*.py',
    '../../**/!(node_modules)/**/*.js',
    './src/**/*.{html,js}'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
