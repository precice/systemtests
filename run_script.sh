# mkdir -p local_logs;
# echo "Created log folder"
# python build_precice.py --dockerfile precice/Dockerfile.Ubuntu1804.home --petsc yes --docker-username precice > local_logs/precice.log 2>&1;
# echo "Built preCICE w/ PETSc"
# python build_adapter.py --dockerfile adapters/Dockerfile.openfoam-adapter.Ubuntu1804 --operating-system ubuntu1804 --precice-installation home --petsc yes --docker-username precice > local_logs/ofadapter.log 2>&1;
# echo "Built OF adapter"
python build_adapter.py --dockerfile adapters/Dockerfile.calculix-adapter --operating-system ubuntu1804 --precice-installation home --petsc yes --docker-username precice -ab makefile-dep-apt > local_logs/ccxadapter.log 2>&1;
echo "Built ccx adapter"
# python system_testing.py -s of-ccx_fsi --base Ubuntu1804.home.PETSc -v > local_logs/test.log 2>&1;
# echo "Finished test, script done!"
