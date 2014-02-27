from setuptools import setup, find_packages

setup(
    name='django-filebrowser',
    version='3.1-no-grappelli-3',
    description='Media-Management with the Django Admin-Interface.',
    author='Burak Emre Kabakcı',
    author_email='emrekabakci@gmail.com',
    url='https://github.com/buremba/django-filebrowser-admintools',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['templates/filebrowser/*.html',
                       'templates/filebrowser/include/*.html',
                       'media/filebrowser/css/*.css',
                       'media/filebrowser/img/*.gif',
                       'media/filebrowser/img/*.png',
                       'media/filebrowser/js/*.js',
                       'media/filebrowser/uploadify/*.*',
                       'media/filebrowser/uploadify/**/*.*']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)