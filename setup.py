setup(
    name="Axialtomographie",
    version="1.0.0",
    description="Korrigiert Axialtomografiedaten",
    author="Elias",
    packages=["Code"],
    include_package_data=True,
    install_requires=[
        "SimpleITK", "tifffile", "matplotlib", "cv2", "numpy", "PIL",
         "skimage", "scipy", "PySimpleGUI","vtk","open3D"
    ],
    entry_points={"console_scripts": ["Code.__main__:main"]},
)
