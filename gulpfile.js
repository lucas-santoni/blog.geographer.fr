const { exec } = require('child_process');

const gulp = require('gulp');
const htmlmin = require('gulp-htmlmin');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const babel = require('gulp-babel');
const bro = require('gulp-bro');
const workboxBuild = require('workbox-build');

// Convert JS files to ES5 using Babel
gulp.task('es5', () =>
  gulp
    .src('public/**/*.js')
    .pipe(
      babel({
        presets: ['@babel/preset-env'],
        compact: true,
      })
    )
    .pipe(gulp.dest('public/'))
);

// Compress JS
gulp.task('uglify', () =>
  gulp.src(['public/**/*.js']).pipe(uglify()).pipe(gulp.dest('public/'))
);

// Bundle JS
gulp.task('browserify', () =>
  gulp.src('theme/static/*.js').pipe(bro()).pipe(gulp.dest('public/'))
);

// Compress HTML
gulp.task('minify-html', () =>
  gulp
    .src('public/**/*.html')
    .pipe(
      htmlmin({
        collapseWhitespace: true,
        removeComments: true,
        minifyCSS: true,
        minifyJS: true,
      })
    )
    .pipe(gulp.dest('public/'))
);

// Compress CSS
gulp.task('minify-css', () =>
  gulp
    .src('public/**/*.css')
    .pipe(cleanCSS({ level: 2 }))
    .pipe(gulp.dest('public/'))
);

// Generate a service-worker
gulp.task('service-worker', () =>
  workboxBuild.generateSW({
    skipWaiting: true, // Use new SW as soon as possible
    cleanupOutdatedCaches: true, // Delete older caches
    sourcemap: false, // Do not generate a source map for the SW
    mode: 'production', // I think it's the default anyway
    offlineGoogleAnalytics: true, // Not a big deal
    navigateFallback: '/404.html', // When we don't have the thing in cache
    navigationPreload: false, // We don't need it as we precache everything
    globDirectory: 'public/', // Where our files are
    globPatterns: [
      '**/*.{html,css,js}',
      'apple-touch-icon.png',
      'favicon.ico',
      'manifest.json',
      'robots.txt',
      'rss.xml',
      'sitemap.xml',
    ], // Are precached
    // globIgnores: [''], // Will never be cached
    swDest: 'public/service-worker.js', // The SW destination
    runtimeCaching: [
      {
        urlPattern: /\.(?:gif|ico|jpg|jpeg|pgm|png)$/, // Cached at runtime
        handler: 'CacheFirst',
        options: {
          cacheName: 'resources',
          expiration: {
            maxEntries: 50,
          },
        },
      },
    ],
  })
);

gulp.task('content', cb =>
  exec('pelican content -o public -s pelicanconf.py', (err, stdout, stderr) => {
    // eslint-disable-next-line no-console
    console.log(stdout);
    // eslint-disable-next-line no-console
    console.log(stderr);
    cb(err);
  })
);

// The order is important, as uglify only works with ES5
gulp.task('minify-js', gulp.series('browserify', 'es5', 'uglify'));

// Can be run in parallel
gulp.task('minify', gulp.parallel('minify-js', 'minify-html', 'minify-css'));

// The service-worker generation has to run last
gulp.task('default', gulp.series('content', 'minify', 'service-worker'));

// Watch for new files while developing
gulp.task('dev', () =>
  gulp.watch(
    [
      'content/**/*',
      'theme/**/*',
      'extensions/**/*',
      'plugins/**/*',
      'pelicanconf.py',
    ],
    { ignoreInitial: false },
    gulp.series('content', 'browserify', 'service-worker')
  )
);
