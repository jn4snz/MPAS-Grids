# ******* step 5: Add initial conditions
mpirun -np 2 ocean_init_model
mv output.0000-01-01_00.00.00.nc grid.nc
