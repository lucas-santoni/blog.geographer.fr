const gulp = require('gulp');
const htmlmin = require('gulp-htmlmin');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const babel = require('gulp-babel');
const bro = require('gulp-bro');

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

gulp.task('uglify', () =>
  gulp.src(['public/**/*.js']).pipe(uglify()).pipe(gulp.dest('public/'))
);

gulp.task('browserify', () =>
  gulp.src('theme/static/*.js').pipe(bro()).pipe(gulp.dest('public/'))
);

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

gulp.task('minify-css', () =>
  gulp
    .src('public/**/*.css')
    .pipe(cleanCSS({ level: 2 }))
    .pipe(gulp.dest('public/'))
);

gulp.task('minify-js', gulp.series('browserify', 'es5', 'uglify'));

gulp.task('default', gulp.parallel('minify-js', 'minify-html', 'minify-css'));
