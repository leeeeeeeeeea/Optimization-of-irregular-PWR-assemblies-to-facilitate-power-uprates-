
% Increase counter:

if (exist('idx', 'var'));
  idx = idx + 1;
else;
  idx = 1;
end;

% Version, title and date:

VERSION                   (idx, [1: 14])  = 'Serpent 2.1.31' ;
COMPILE_DATE              (idx, [1: 20])  = 'Oct 23 2021 12:26:58' ;
DEBUG                     (idx, 1)        = 0 ;
TITLE                     (idx, [1: 13])  = 'BL324 asembly' ;
CONFIDENTIAL_DATA         (idx, 1)        = 0 ;
INPUT_FILE_NAME           (idx, [1:  9])  = 'BL324_1_8' ;
WORKING_DIRECTORY         (idx, [1: 45])  = '/home/lg779/Small_optimisation_my_subchan_1_8' ;
HOSTNAME                  (idx, [1: 17])  = 'ray.eng.cam.ac.uk' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E5-2650 v2 @ 2.60GHz' ;
CPU_MHZ                   (idx, 1)        = 1070.0 ;
START_DATE                (idx, [1: 24])  = 'Fri Jul 24 18:51:38 2026' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Fri Jul 24 18:57:06 2026' ;

% Run parameters:

POP                       (idx, 1)        = 10000 ;
CYCLES                    (idx, 1)        = 1000 ;
SKIP                      (idx, 1)        = 5 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1784915498718 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 0 ;
B1_CALCULATION            (idx, [1:  3])  = [ 0 0 0 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 0 ;
IMPLICIT_REACTION_RATES   (idx, 1)        = 1 ;

% Optimization:

OPTIMIZATION_MODE         (idx, 1)        = 4 ;
RECONSTRUCT_MICROXS       (idx, 1)        = 1 ;
RECONSTRUCT_MACROXS       (idx, 1)        = 1 ;
DOUBLE_INDEXING           (idx, 1)        = 0 ;
MG_MAJORANT_MODE          (idx, 1)        = 0 ;

% Parallelization:

MPI_TASKS                 (idx, 1)        = 1 ;
OMP_THREADS               (idx, 1)        = 10 ;
MPI_REPRODUCIBILITY       (idx, 1)        = 0 ;
OMP_REPRODUCIBILITY       (idx, 1)        = 1 ;
OMP_HISTORY_PROFILE       (idx, [1:  10]) = [  1.09902E+00  9.91298E-01  9.79888E-01  9.95081E-01  9.82267E-01  9.95181E-01  9.90766E-01  9.89243E-01  9.77760E-01  9.99498E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 62])  = '/usr/software/mcnplib/SERPENT/XSdata_endfb7/sss_endfb7u.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1:  3])  = 'N/A' ;
SFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
NFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 2.2E-09  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  2.52242E-02 0.00045  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  9.74776E-01 1.2E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  7.66585E-01 3.7E-05  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  7.67114E-01 3.7E-05  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  2.74167E+00 0.00015  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  2.76708E+01 0.00017  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  2.76708E+01 0.00017  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  8.40054E+00 0.00023  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  8.47459E-01 0.00049  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 1000 ;
SIMULATED_HISTORIES       (idx, 1)        = 10000778 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  1.00008E+04 0.00040 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  1.00008E+04 0.00040 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  4.17584E+01 ;
RUNNING_TIME              (idx, 1)        =  5.47162E+00 ;
INIT_TIME                 (idx, [1:  2])  = [  1.77667E-02  1.77667E-02 ];
PROCESS_TIME              (idx, [1:  2])  = [  2.83337E-04  2.83337E-04 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  5.45357E+00  5.45357E+00  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  5.47147E+00  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 7.63182 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  7.83418E+00 0.00473 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  9.54651E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 48219.61 ;
ALLOC_MEMSIZE             (idx, 1)        = 259.89;
MEMSIZE                   (idx, 1)        = 139.60;
XS_MEMSIZE                (idx, 1)        = 58.21;
MAT_MEMSIZE               (idx, 1)        = 10.33;
RES_MEMSIZE               (idx, 1)        = 0.55;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 70.51;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 120.29;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 156 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  0.00000E+00 ;
NEUTRON_ERG_NE            (idx, 1)        = 89940 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.00000E+37 ;
URES_EMAX                 (idx, 1)        = -1.00000E+37 ;
URES_AVAIL                (idx, 1)        = 3 ;
URES_USED                 (idx, 1)        = 0 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 7 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 7 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 0 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 162 ;
TOT_TRANSMU_REA           (idx, 1)        = 0 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 0 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 0 ;
TMS_MODE                  (idx, 1)        = 0 ;
SAMPLE_FISS               (idx, 1)        = 1 ;
SAMPLE_CAPT               (idx, 1)        = 1 ;
SAMPLE_SCATT              (idx, 1)        = 1 ;

% Radioactivity data:

TOT_ACTIVITY              (idx, 1)        =  0.00000E+00 ;
TOT_DECAY_HEAT            (idx, 1)        =  0.00000E+00 ;
TOT_SF_RATE               (idx, 1)        =  0.00000E+00 ;
ACTINIDE_ACTIVITY         (idx, 1)        =  0.00000E+00 ;
ACTINIDE_DECAY_HEAT       (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_ACTIVITY  (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_DECAY_HEAT(idx, 1)        =  0.00000E+00 ;
INHALATION_TOXICITY       (idx, 1)        =  0.00000E+00 ;
INGESTION_TOXICITY        (idx, 1)        =  0.00000E+00 ;
ACTINIDE_INH_TOX          (idx, 1)        =  0.00000E+00 ;
ACTINIDE_ING_TOX          (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_INH_TOX   (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_ING_TOX   (idx, 1)        =  0.00000E+00 ;
SR90_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
TE132_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
I131_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
I132_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
CS134_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
CS137_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
PHOTON_DECAY_SOURCE       (idx, 1)        =  0.00000E+00 ;
NEUTRON_DECAY_SOURCE      (idx, 1)        =  0.00000E+00 ;
ALPHA_DECAY_SOURCE        (idx, 1)        =  0.00000E+00 ;
ELECTRON_DECAY_SOURCE     (idx, 1)        =  0.00000E+00 ;

% Normalization coefficient:

NORM_COEF                 (idx, [1:   4]) = [  1.17145E+13 0.00030  0.00000E+00 0.0E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  3.62182E-01 0.00075 ];
U235_FISS                 (idx, [1:   4]) = [  6.48042E+16 0.00034  9.50190E-01 9.7E-05 ];
U238_FISS                 (idx, [1:   4]) = [  3.39749E+15 0.00195  4.98096E-02 0.00186 ];
U235_CAPT                 (idx, [1:   4]) = [  1.49847E+16 0.00084  3.05056E-01 0.00075 ];
U238_CAPT                 (idx, [1:   4]) = [  2.88984E+16 0.00071  5.88250E-01 0.00040 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 10000778 1.00000E+07 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.55016E+04 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 10000778 1.00155E+07 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 4187155 4.19338E+06 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 5813623 5.82213E+06 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 10000778 1.00155E+07 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 -1.19209E-07 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   2]) = [  2.21250E+06 0.0E+00 ];
TOT_POWDENS               (idx, [1:   2]) = [  1.20875E+01 0.0E+00 ];
TOT_GENRATE               (idx, [1:   2]) = [  1.67526E+17 6.5E-06 ];
TOT_FISSRATE              (idx, [1:   2]) = [  6.81922E+16 7.2E-07 ];
TOT_CAPTRATE              (idx, [1:   2]) = [  4.91400E+16 0.00030 ];
TOT_ABSRATE               (idx, [1:   2]) = [  1.17332E+17 0.00013 ];
TOT_SRCRATE               (idx, [1:   2]) = [  1.17145E+17 0.00030 ];
TOT_FLUX                  (idx, [1:   2]) = [  5.03705E+18 0.00026 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  1.17332E+17 0.00013 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  3.24618E+18 0.00021 ];
INI_FMASS                 (idx, 1)        =  1.83040E-01 ;
TOT_FMASS                 (idx, 1)        =  1.83040E-01 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.91059E+00 0.00022 ];
SIX_FF_F                  (idx, [1:   2]) = [  9.47439E-01 9.6E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  6.03538E-01 0.00026 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  1.30931E+00 0.00024 ];
SIX_FF_LF                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_LT                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.43034E+00 0.00027 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.43034E+00 0.00027 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.45667E+00 7.1E-06 ];
FISSE                     (idx, [1:   2]) = [  2.02506E+02 7.2E-07 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.43054E+00 0.00029  1.42063E+00 0.00027  9.71112E-03 0.00475 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.43005E+00 0.00013 ];
COL_KEFF                  (idx, [1:   2]) = [  1.43021E+00 0.00030 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.43005E+00 0.00013 ];
ABS_KINF                  (idx, [1:   2]) = [  1.43005E+00 0.00013 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.72837E+01 0.00011 ];
IMP_ALF                   (idx, [1:   2]) = [  1.72853E+01 5.2E-05 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  6.24723E-07 0.00198 ];
IMP_EALF                  (idx, [1:   2]) = [  6.22726E-07 0.00090 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  1.79130E-01 0.00197 ];
IMP_AFGE                  (idx, [1:   2]) = [  1.78546E-01 0.00077 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 6 ;
FWD_ANA_BETA_ZERO         (idx, [1:  14]) = [  4.89748E-03 0.00371  1.38996E-04 0.02180  7.77348E-04 0.00935  7.73255E-04 0.00946  2.26098E-03 0.00576  7.18943E-04 0.00976  2.27955E-04 0.01810 ];
FWD_ANA_LAMBDA            (idx, [1:  14]) = [  7.81754E-01 0.00928  1.08544E-02 0.01228  3.16834E-02 0.00013  1.10018E-01 0.00018  3.19947E-01 0.00014  1.34701E+00 0.00011  8.48302E+00 0.00681 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  14]) = [  6.81383E-03 0.00524  1.88876E-04 0.03041  1.07043E-03 0.01316  1.09959E-03 0.01331  3.13344E-03 0.00795  9.96619E-04 0.01335  3.24883E-04 0.02497 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  14]) = [  7.90187E-01 0.01292  1.24907E-02 1.8E-06  3.16832E-02 0.00019  1.09988E-01 0.00023  3.19950E-01 0.00020  1.34678E+00 0.00015  8.85693E+00 0.00134 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  1.34792E-05 0.00063  1.34732E-05 0.00063  1.43552E-05 0.00648 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  1.92808E-05 0.00054  1.92722E-05 0.00054  2.05347E-05 0.00647 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  14]) = [  6.78912E-03 0.00494  1.87430E-04 0.03070  1.05855E-03 0.01323  1.07942E-03 0.01289  3.14355E-03 0.00758  1.00108E-03 0.01291  3.19099E-04 0.02420 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  14]) = [  7.86013E-01 0.01260  1.24907E-02 2.1E-06  3.16800E-02 0.00021  1.10006E-01 0.00025  3.20011E-01 0.00020  1.34671E+00 0.00017  8.84830E+00 0.00148 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  1.33174E-05 0.00347  1.33091E-05 0.00347  1.44136E-05 0.01608 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  1.90486E-05 0.00345  1.90367E-05 0.00345  2.06168E-05 0.01610 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  14]) = [  6.74908E-03 0.01490  1.99038E-04 0.08945  1.07987E-03 0.03793  1.07510E-03 0.03590  3.08700E-03 0.02206  1.00673E-03 0.03753  3.01343E-04 0.06868 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  14]) = [  7.68237E-01 0.03427  1.24908E-02 5.0E-06  3.16895E-02 0.00045  1.10024E-01 0.00059  3.19949E-01 0.00054  1.34692E+00 0.00035  8.87592E+00 0.00320 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  14]) = [  6.70785E-03 0.01435  1.94550E-04 0.08881  1.08091E-03 0.03683  1.07383E-03 0.03505  3.04888E-03 0.02124  1.00968E-03 0.03645  3.00012E-04 0.06797 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  14]) = [  7.65806E-01 0.03370  1.24908E-02 5.1E-06  3.16877E-02 0.00045  1.10015E-01 0.00058  3.19935E-01 0.00052  1.34692E+00 0.00035  8.87521E+00 0.00320 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -5.08393E+02 0.01471 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  1.34692E-05 0.00068 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  1.92666E-05 0.00061 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  6.82497E-03 0.00289 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -5.06736E+02 0.00283 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  3.55716E-07 0.00036 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  2.90541E-06 0.00032  2.90549E-06 0.00032  2.89397E-06 0.00372 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.18989E-05 0.00039  2.19000E-05 0.00039  2.17392E-05 0.00490 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  6.04114E-01 0.00026  6.02685E-01 0.00026  9.06089E-01 0.00589 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.02212E+01 0.00886 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  2.76708E+01 0.00017  3.04460E+01 0.00021 ];

