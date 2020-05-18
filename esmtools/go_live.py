bmln = [ EPU57.gap, EPU57.phase, EPU105.gap, EPU105.phase, FEslit.h_center, FEslit.h_gap, FEslit.v_center, 
FEslit.v_gap, M1.X, M1.Ry, M1.Rz, PGM.Energy, PGM.Focus_Const, PGM.Grating_Trans, M3Udiag.trans, 
M3.X, M3.Y, M3.Z, M3.Rx, M3.Ry, M3.Rz, ExitSlitA.h_gap, ExitSlitA.v_gap, ExitSlitB.h_gap, ExitSlitB.v_gap, 
BTA2diag.trans, BTB2diag.trans, M4A.HFM_X, M4A.HFM_Z,  M4A.VFM_Y, M4A.VFM_Z]    


scan_esm = [scan_1D, scan_multi_1D, scan_2D]

from esmtools import MyApp_window 


MyApp_window.main(db=db, RE=RE, print_summary=print_summary, scan_time=None,  scan_esm=scan_esm, 
motors =bmln, Beamline=Beamline, BeamSource = BeamSource) 
