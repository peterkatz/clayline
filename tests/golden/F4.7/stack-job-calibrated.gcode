; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=stack-job-calibrated
; prepared_trace_sha256=e4883b55e20d9e8bcc9baedb073a6304f993c148baa928b79e6d8193761e572c
; body_sha256=76e7c520090d92c2e8178495c3f5e68555c3a8887a4ba9186f6b5d2bfe9c4b7c
; profile_name=potterbot-xl
; profile_version=1.3.0
; profile_verified=true
; profile_flavor=marlin
; extrusion_mode=absolute
; bead_width_mm=5
; layer_height_mm=2
; flow_multiplier=1
; wet_density_g_cm3=1.8
; prime_mm=15
; end_early_mm=5
; first_layer_z_mm=2
; speed_default_mm_s=40
; speed_first_layer_mm_s=30
; speed_travel_mm_s=40
; virtual_filament_diameter_mm=1.75
; work_bounds=17,398,12,393,0,710
; machine_envelope=0,490,0,490,0,710
; stats.motion_count=2885
; stats.print_motion_count=2878
; stats.travel_motion_count=7
; stats.stroke_count=4
; stats.page_count=2
; stats.print_path_mm=4978.817205
; stats.deposited_path_mm=4958.817205
; stats.travel_path_mm=230.632653
; stats.total_motion_path_mm=5209.449858
; stats.motion_time_seconds=149.432595
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=149.432595
; stats.body_volume_mm3=51579.233837
; stats.wet_weight_g=92.842621
; stats.body_e=21444.153537
; stats.pressure_e_excluded=0
; stats.warning_count=41
; nominal_label=calibrated centerline
; stats.warning_count.over_void=16
; stats.warning_count.tight_radius=10
; stats.warning_count.under_spaced=15
; parameter.alternate=true
; parameter.collision_lift=bounded-clearance-v1
; parameter.first_layer_flow_factor=1.1
; parameter.first_layer_height=2.0
; parameter.first_layer_speed_factor=0.6
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.joint_boost=0.0
; parameter.layers=2
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_mode=stack
; parameter.page_pause_seconds=disabled
; parameter.page_travel_clearance=50.0
; parameter.page_travel_lift=4.0
; parameter.provisional_flow_multiplier=1.0
; parameter.stack_job_page_count=2
; parameter.stack_page_0_datum_top_z_mm=4.0
; parameter.stack_page_0_material_z_max_mm=4.0
; parameter.stack_page_0_material_z_min_mm=2.0
; parameter.stack_page_0_nominal_path_start_z_mm=2.0
; parameter.stack_page_0_nominal_top_z_mm=4.0
; parameter.stack_page_0_path_start_z_mm=2.0
; parameter.stack_page_0_z_max_mm=4.0
; parameter.stack_page_0_z_min_mm=2.0
; parameter.stack_page_1_datum_top_z_mm=8.0
; parameter.stack_page_1_material_z_max_mm=10.0
; parameter.stack_page_1_material_z_min_mm=6.0
; parameter.stack_page_1_nominal_path_start_z_mm=6.0
; parameter.stack_page_1_nominal_top_z_mm=8.0
; parameter.stack_page_1_path_start_z_mm=6.0
; parameter.stack_page_1_prior_datum_top_z_mm=4.0
; parameter.stack_page_1_z_max_mm=12.0
; parameter.stack_page_1_z_min_mm=6.0
; parameter.stack_page_material_height_mm=4.0
; parameter.stack_total_height_mm=10.0
; parameter.standoff_z=20.0
; parameter.z_mode=calibrated
; parameter.z_modulation=0.0
; parameter.z_step_per_layer=2.0
; pressure_management=profile and marked pressure blocks excluded from body volume
; thermal_policy=no heater or fan commands outside verbatim profile blocks
; CLAYLINE_HEADER_END
; CLAYLINE_PROFILE_START_BEGIN
M105
M109 S0
M82 ;absolute extrusion mode
G28 ;Home
G1 X207.5 Y202.5 Z20 F10000 ;Move X and Y to center, Z to 20mm high
G92 E0
G1 E100 F40000 ; Prime Extruder (v1.3.0: matches the reduced end-of-job depressurize)
G92 E0
G92 E0
G92 E0
M107
; CLAYLINE_PROFILE_START_END
; CLAYLINE_BODY_BEGIN
G21 ; clayline units: millimeters
G90 ; clayline absolute XYZ
M82 ; clayline absolute extrusion
G92 E0 ; clayline body extrusion origin
; CLAYLINE_PAGE index=0
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-0-rings-grid-base page_name=rings-grid-base z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X136.448281 Y131.448281 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start XY at safe Z
G0 X136.448281 Y131.448281 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0000 note=stroke start vertical approach
G1 X135.440942 Y132.559707 Z2 E0.342995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X135.152614 Y132.877828 Z2 E0.567445 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X134.514824 Y133.737789 Z2 E1.371981 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X134.003307 Y134.427489 Z2 E2.269778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X133.673604 Y134.977566 Z2 E3.086956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X133.011428 Y136.08234 Z2 E5.107001 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X132.920796 Y136.273965 Z2 E5.487922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X132.279463 Y137.629949 Z2 E8.574879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X132.186528 Y137.826444 Z2 E9.079113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X131.754421 Y139.034102 Z2 E12.347825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X131.536553 Y139.643003 Z2 E14.186113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X131.329219 Y140.470726 Z2 E16.806762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X131.067761 Y141.514524 Z2 E20.428003 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X131.005554 Y141.93389 Z2 E21.951689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X130.785459 Y143.417655 Z2 E27.782607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X130.784668 Y143.422983 Z2 E27.804782 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X130.711331 Y144.915796 Z2 E34.299514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X130.69 Y145.35 Z2 E36.287641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.784668 Y147.277017 Z2 E45.111035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.067761 Y149.185476 Z2 E53.934429 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.536553 Y151.056997 Z2 E62.757824 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X132.186528 Y152.873556 Z2 E71.581218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.011428 Y154.61766 Z2 E80.404612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.003307 Y156.272511 Z2 E89.228007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.152614 Y157.822172 Z2 E98.051401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.448281 Y159.251719 Z2 E106.874795 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.877828 Y160.547386 Z2 E115.69819 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.427489 Y161.696693 Z2 E124.521584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.08234 Y162.688572 Z2 E133.344978 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.826444 Y163.513472 Z2 E142.168373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.643003 Y164.163447 Z2 E150.991767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.514524 Y164.632239 Z2 E159.815161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.422983 Y164.915332 Z2 E168.638556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.35 Y165.01 Z2 E177.46195 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.277017 Y164.915332 Z2 E186.285344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.185476 Y164.632239 Z2 E195.108739 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.112624 Y164.4 Z2 E199.479834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.185476 Y164.167761 Z2 E203.85093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.277017 Y163.884668 Z2 E212.674324 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.35 Y163.79 Z2 E221.497718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.422983 Y163.884668 Z2 E230.321113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.514524 Y164.167761 Z2 E239.144507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.643003 Y164.636553 Z2 E247.967901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.826444 Y165.286528 Z2 E256.791296 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.08234 Y166.111428 Z2 E265.61469 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.427489 Y167.103307 Z2 E274.438084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.877828 Y168.252614 Z2 E283.261479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.448281 Y169.548281 Z2 E292.084873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.152614 Y170.977828 Z2 E300.908267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.003307 Y172.527489 Z2 E309.731662 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.011428 Y174.18234 Z2 E318.555056 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X132.186528 Y175.926444 Z2 E327.37845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.536553 Y177.743003 Z2 E336.201845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.067761 Y179.614524 Z2 E345.025239 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.784668 Y181.522983 Z2 E353.848633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.69 Y183.45 Z2 E362.672028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.784668 Y185.377017 Z2 E371.495422 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.067761 Y187.285476 Z2 E380.318816 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.536553 Y189.156997 Z2 E389.142211 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X132.186528 Y190.973556 Z2 E397.965605 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.011428 Y192.71766 Z2 E406.789 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.003307 Y194.372511 Z2 E415.612394 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.152614 Y195.922172 Z2 E424.435788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.448281 Y197.351719 Z2 E433.259183 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.877828 Y198.647386 Z2 E442.082577 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.427489 Y199.796693 Z2 E450.905971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.08234 Y200.788572 Z2 E459.729366 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.826444 Y201.613472 Z2 E468.55276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.643003 Y202.263447 Z2 E477.376154 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.514524 Y202.732239 Z2 E486.199549 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.422983 Y203.015332 Z2 E495.022943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.35 Y203.11 Z2 E503.846337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.277017 Y203.015332 Z2 E512.669732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.185476 Y202.732239 Z2 E521.493126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.112624 Y202.5 Z2 E525.864221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.185476 Y202.267761 Z2 E530.235317 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.277017 Y201.984668 Z2 E539.058711 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.35 Y201.89 Z2 E547.882106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.422983 Y201.984668 Z2 E556.7055 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.514524 Y202.267761 Z2 E565.528894 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.643003 Y202.736553 Z2 E574.352289 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.826444 Y203.386528 Z2 E583.175683 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.08234 Y204.211428 Z2 E591.999077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.427489 Y205.203307 Z2 E600.822472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.877828 Y206.352614 Z2 E609.645866 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.448281 Y207.648281 Z2 E618.46926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.152614 Y209.077828 Z2 E627.292655 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.003307 Y210.627489 Z2 E636.116049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.011428 Y212.28234 Z2 E644.939443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X132.186528 Y214.026444 Z2 E653.762838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.536553 Y215.843003 Z2 E662.586232 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.067761 Y217.714524 Z2 E671.409626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.784668 Y219.622983 Z2 E680.233021 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.69 Y221.55 Z2 E689.056415 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.784668 Y223.477017 Z2 E697.879809 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.067761 Y225.385476 Z2 E706.703204 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.536553 Y227.256997 Z2 E715.526598 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X132.186528 Y229.073556 Z2 E724.349992 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.011428 Y230.81766 Z2 E733.173387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.003307 Y232.472511 Z2 E741.996781 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.152614 Y234.022172 Z2 E750.820175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.448281 Y235.451719 Z2 E759.64357 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.877828 Y236.747386 Z2 E768.466964 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.427489 Y237.896693 Z2 E777.290359 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.08234 Y238.888572 Z2 E786.113753 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.826444 Y239.713472 Z2 E794.937147 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.643003 Y240.363447 Z2 E803.760542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.514524 Y240.832239 Z2 E812.583936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.422983 Y241.115332 Z2 E821.40733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.35 Y241.21 Z2 E830.230725 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.277017 Y241.115332 Z2 E839.054119 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.185476 Y240.832239 Z2 E847.877513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.112624 Y240.6 Z2 E852.248609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.185476 Y240.367761 Z2 E856.619704 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.277017 Y240.084668 Z2 E865.443098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.35 Y239.99 Z2 E874.266493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.422983 Y240.084668 Z2 E883.089887 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.514524 Y240.367761 Z2 E891.913281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.643003 Y240.836553 Z2 E900.736676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.826444 Y241.486528 Z2 E909.56007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.08234 Y242.311428 Z2 E918.383465 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.427489 Y243.303307 Z2 E927.206859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.877828 Y244.452614 Z2 E936.030253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.448281 Y245.748281 Z2 E944.853648 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.152614 Y247.177828 Z2 E953.677042 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.003307 Y248.727489 Z2 E962.500436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.011428 Y250.38234 Z2 E971.323831 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X132.186528 Y252.126444 Z2 E980.147225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.536553 Y253.943003 Z2 E988.970619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.067761 Y255.814524 Z2 E997.794014 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.784668 Y257.722983 Z2 E1006.617408 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.69 Y259.65 Z2 E1015.440802 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.784668 Y261.577017 Z2 E1024.264197 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.067761 Y263.485476 Z2 E1033.087591 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.536553 Y265.356997 Z2 E1041.910985 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X132.186528 Y267.173556 Z2 E1050.73438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.011428 Y268.91766 Z2 E1059.557774 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.003307 Y270.572511 Z2 E1068.381168 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.152614 Y272.122172 Z2 E1077.204563 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.448281 Y273.551719 Z2 E1086.027957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.877828 Y274.847386 Z2 E1094.851351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.427489 Y275.996693 Z2 E1103.674746 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.08234 Y276.988572 Z2 E1112.49814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.826444 Y277.813472 Z2 E1121.321534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.643003 Y278.463447 Z2 E1130.144929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.514524 Y278.932239 Z2 E1138.968323 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.422983 Y279.215332 Z2 E1147.791718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.35 Y279.31 Z2 E1156.615112 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.277017 Y279.215332 Z2 E1165.438506 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.185476 Y278.932239 Z2 E1174.261901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.056997 Y278.463447 Z2 E1183.085295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.873556 Y277.813472 Z2 E1191.908689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.61766 Y276.988572 Z2 E1200.732084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.272511 Y275.996693 Z2 E1209.555478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.822172 Y274.847386 Z2 E1218.378872 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.251719 Y273.551719 Z2 E1227.202267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.547386 Y272.122172 Z2 E1236.025661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.696693 Y270.572511 Z2 E1244.849055 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.688572 Y268.91766 Z2 E1253.67245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.513472 Y267.173556 Z2 E1262.495844 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.163447 Y265.356997 Z2 E1271.319238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.632239 Y263.485476 Z2 E1280.142633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.915332 Y261.577017 Z2 E1288.966027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.01 Y259.65 Z2 E1297.789421 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.915332 Y257.722983 Z2 E1306.612816 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.632239 Y255.814524 Z2 E1315.43621 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.4 Y254.887376 Z2 E1319.807305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.167761 Y255.814524 Z2 E1324.178401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.884668 Y257.722983 Z2 E1333.001795 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.79 Y259.65 Z2 E1341.82519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.884668 Y261.577017 Z2 E1350.648584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.167761 Y263.485476 Z2 E1359.471978 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.636553 Y265.356997 Z2 E1368.295373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.286528 Y267.173556 Z2 E1377.118767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.111428 Y268.91766 Z2 E1385.942161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.103307 Y270.572511 Z2 E1394.765556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.252614 Y272.122172 Z2 E1403.58895 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548281 Y273.551719 Z2 E1412.412344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.977828 Y274.847386 Z2 E1421.235739 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.527489 Y275.996693 Z2 E1430.059133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X179.18234 Y276.988572 Z2 E1438.882527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.926444 Y277.813472 Z2 E1447.705922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.743003 Y278.463447 Z2 E1456.529316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.614524 Y278.932239 Z2 E1465.35271 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.522983 Y279.215332 Z2 E1474.176105 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.45 Y279.31 Z2 E1482.999499 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.377017 Y279.215332 Z2 E1491.822893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.285476 Y278.932239 Z2 E1500.646288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.156997 Y278.463447 Z2 E1509.469682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.973556 Y277.813472 Z2 E1518.293076 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X197.71766 Y276.988572 Z2 E1527.116471 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.372511 Y275.996693 Z2 E1535.939865 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.922172 Y274.847386 Z2 E1544.76326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.351719 Y273.551719 Z2 E1553.586654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.647386 Y272.122172 Z2 E1562.410048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.796693 Y270.572511 Z2 E1571.233443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.788572 Y268.91766 Z2 E1580.056837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.613472 Y267.173556 Z2 E1588.880231 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.263447 Y265.356997 Z2 E1597.703626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.732239 Y263.485476 Z2 E1606.52702 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.015332 Y261.577017 Z2 E1615.350414 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.11 Y259.65 Z2 E1624.173809 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.015332 Y257.722983 Z2 E1632.997203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.732239 Y255.814524 Z2 E1641.820597 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y254.887376 Z2 E1646.191693 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.267761 Y255.814524 Z2 E1650.562788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.984668 Y257.722983 Z2 E1659.386183 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.89 Y259.65 Z2 E1668.209577 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.984668 Y261.577017 Z2 E1677.032971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.267761 Y263.485476 Z2 E1685.856366 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.736553 Y265.356997 Z2 E1694.67976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.386528 Y267.173556 Z2 E1703.503154 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.211428 Y268.91766 Z2 E1712.326549 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.203307 Y270.572511 Z2 E1721.149943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.352614 Y272.122172 Z2 E1729.973337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.648281 Y273.551719 Z2 E1738.796732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.077828 Y274.847386 Z2 E1747.620126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.627489 Y275.996693 Z2 E1756.44352 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.28234 Y276.988572 Z2 E1765.266915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.026444 Y277.813472 Z2 E1774.090309 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.843003 Y278.463447 Z2 E1782.913703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.714524 Y278.932239 Z2 E1791.737098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.622983 Y279.215332 Z2 E1800.560492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.55 Y279.31 Z2 E1809.383886 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.477017 Y279.215332 Z2 E1818.207281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X230.385476 Y278.932239 Z2 E1827.030675 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.256997 Y278.463447 Z2 E1835.854069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.073556 Y277.813472 Z2 E1844.677464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.81766 Y276.988572 Z2 E1853.500858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.472511 Y275.996693 Z2 E1862.324252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.022172 Y274.847386 Z2 E1871.147647 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.451719 Y273.551719 Z2 E1879.971041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.747386 Y272.122172 Z2 E1888.794435 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.896693 Y270.572511 Z2 E1897.61783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.888572 Y268.91766 Z2 E1906.441224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.713472 Y267.173556 Z2 E1915.264619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.363447 Y265.356997 Z2 E1924.088013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.832239 Y263.485476 Z2 E1932.911407 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.115332 Y261.577017 Z2 E1941.734802 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.21 Y259.65 Z2 E1950.558196 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.115332 Y257.722983 Z2 E1959.38159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.832239 Y255.814524 Z2 E1968.204985 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.6 Y254.887376 Z2 E1972.57608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.367761 Y255.814524 Z2 E1976.947175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.084668 Y257.722983 Z2 E1985.77057 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.99 Y259.65 Z2 E1994.593964 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.084668 Y261.577017 Z2 E2003.417358 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.367761 Y263.485476 Z2 E2012.240753 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.836553 Y265.356997 Z2 E2021.064147 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.486528 Y267.173556 Z2 E2029.887542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.311428 Y268.91766 Z2 E2038.710936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.303307 Y270.572511 Z2 E2047.53433 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.452614 Y272.122172 Z2 E2056.357725 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.748281 Y273.551719 Z2 E2065.181119 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.177828 Y274.847386 Z2 E2074.004513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.727489 Y275.996693 Z2 E2082.827908 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.38234 Y276.988572 Z2 E2091.651302 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.126444 Y277.813472 Z2 E2100.474696 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.943003 Y278.463447 Z2 E2109.298091 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.814524 Y278.932239 Z2 E2118.121485 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.722983 Y279.215332 Z2 E2126.944879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.65 Y279.31 Z2 E2135.768274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.577017 Y279.215332 Z2 E2144.591668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.485476 Y278.932239 Z2 E2153.415062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.356997 Y278.463447 Z2 E2162.238457 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.173556 Y277.813472 Z2 E2171.061851 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.91766 Y276.988572 Z2 E2179.885245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.572511 Y275.996693 Z2 E2188.70864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.122172 Y274.847386 Z2 E2197.532034 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.551719 Y273.551719 Z2 E2206.355428 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.847386 Y272.122172 Z2 E2215.178823 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.996693 Y270.572511 Z2 E2224.002217 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.988572 Y268.91766 Z2 E2232.825611 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X282.813472 Y267.173556 Z2 E2241.649006 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.463447 Y265.356997 Z2 E2250.4724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.932239 Y263.485476 Z2 E2259.295794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.215332 Y261.577017 Z2 E2268.119189 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.31 Y259.65 Z2 E2276.942583 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.215332 Y257.722983 Z2 E2285.765978 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.932239 Y255.814524 Z2 E2294.589372 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.463447 Y253.943003 Z2 E2303.412766 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X282.813472 Y252.126444 Z2 E2312.236161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.988572 Y250.38234 Z2 E2321.059555 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.996693 Y248.727489 Z2 E2329.882949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.847386 Y247.177828 Z2 E2338.706344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.551719 Y245.748281 Z2 E2347.529738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.122172 Y244.452614 Z2 E2356.353132 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.572511 Y243.303307 Z2 E2365.176527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.91766 Y242.311428 Z2 E2373.999921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.173556 Y241.486528 Z2 E2382.823315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.356997 Y240.836553 Z2 E2391.64671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.412624 Y240.6 Z2 E2396.099009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.356997 Y240.363447 Z2 E2400.551308 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.173556 Y239.713472 Z2 E2409.374702 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.91766 Y238.888572 Z2 E2418.198096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.572511 Y237.896693 Z2 E2427.021491 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.122172 Y236.747386 Z2 E2435.844885 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.551719 Y235.451719 Z2 E2444.668279 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.847386 Y234.022172 Z2 E2453.491674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.996693 Y232.472511 Z2 E2462.315068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.988572 Y230.81766 Z2 E2471.138462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X282.813472 Y229.073556 Z2 E2479.961857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.463447 Y227.256997 Z2 E2488.785251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.932239 Y225.385476 Z2 E2497.608645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.215332 Y223.477017 Z2 E2506.43204 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.31 Y221.55 Z2 E2515.255434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.215332 Y219.622983 Z2 E2524.078828 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.932239 Y217.714524 Z2 E2532.902223 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.463447 Y215.843003 Z2 E2541.725617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X282.813472 Y214.026444 Z2 E2550.549011 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.988572 Y212.28234 Z2 E2559.372406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.996693 Y210.627489 Z2 E2568.1958 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.847386 Y209.077828 Z2 E2577.019194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.551719 Y207.648281 Z2 E2585.842589 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.122172 Y206.352614 Z2 E2594.665983 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.572511 Y205.203307 Z2 E2603.489378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.91766 Y204.211428 Z2 E2612.312772 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.173556 Y203.386528 Z2 E2621.136166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.356997 Y202.736553 Z2 E2629.959561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.412624 Y202.5 Z2 E2634.41186 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.356997 Y202.263447 Z2 E2638.864158 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.173556 Y201.613472 Z2 E2647.687553 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.91766 Y200.788572 Z2 E2656.510947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.572511 Y199.796693 Z2 E2665.334341 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.122172 Y198.647386 Z2 E2674.157736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.551719 Y197.351719 Z2 E2682.98113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.847386 Y195.922172 Z2 E2691.804525 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.996693 Y194.372511 Z2 E2700.627919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.988572 Y192.71766 Z2 E2709.451313 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X282.813472 Y190.973556 Z2 E2718.274708 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.463447 Y189.156997 Z2 E2727.098102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.932239 Y187.285476 Z2 E2735.921496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.215332 Y185.377017 Z2 E2744.744891 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.31 Y183.45 Z2 E2753.568285 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.215332 Y181.522983 Z2 E2762.391679 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.932239 Y179.614524 Z2 E2771.215074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.463447 Y177.743003 Z2 E2780.038468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X282.813472 Y175.926444 Z2 E2788.861862 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.988572 Y174.18234 Z2 E2797.685257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.996693 Y172.527489 Z2 E2806.508651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.847386 Y170.977828 Z2 E2815.332045 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.551719 Y169.548281 Z2 E2824.15544 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.122172 Y168.252614 Z2 E2832.978834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.572511 Y167.103307 Z2 E2841.802228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.91766 Y166.111428 Z2 E2850.625623 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.173556 Y165.286528 Z2 E2859.449017 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.356997 Y164.636553 Z2 E2868.272411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.485476 Y164.167761 Z2 E2877.095806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.577017 Y163.884668 Z2 E2885.9192 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.65 Y163.79 Z2 E2894.742594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.722983 Y163.884668 Z2 E2903.565989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.814524 Y164.167761 Z2 E2912.389383 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.943003 Y164.636553 Z2 E2921.212778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.126444 Y165.286528 Z2 E2930.036172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.38234 Y166.111428 Z2 E2938.859566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.727489 Y167.103307 Z2 E2947.682961 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.177828 Y168.252614 Z2 E2956.506355 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.748281 Y169.548281 Z2 E2965.329749 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.452614 Y170.977828 Z2 E2974.153144 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.303307 Y172.527489 Z2 E2982.976538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.311428 Y174.18234 Z2 E2991.799932 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.486528 Y175.926444 Z2 E3000.623327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.836553 Y177.743003 Z2 E3009.446721 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.367761 Y179.614524 Z2 E3018.270115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.084668 Y181.522983 Z2 E3027.09351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.99 Y183.45 Z2 E3035.916904 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.084668 Y185.377017 Z2 E3044.740298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.367761 Y187.285476 Z2 E3053.563693 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.836553 Y189.156997 Z2 E3062.387087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.486528 Y190.973556 Z2 E3071.210481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.311428 Y192.71766 Z2 E3080.033876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.303307 Y194.372511 Z2 E3088.85727 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.452614 Y195.922172 Z2 E3097.680664 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.748281 Y197.351719 Z2 E3106.504059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.177828 Y198.647386 Z2 E3115.327453 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.727489 Y199.796693 Z2 E3124.150847 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.38234 Y200.788572 Z2 E3132.974242 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.126444 Y201.613472 Z2 E3141.797636 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.943003 Y202.263447 Z2 E3150.621031 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.814524 Y202.732239 Z2 E3159.444425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.722983 Y203.015332 Z2 E3168.267819 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.65 Y203.11 Z2 E3177.091214 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.577017 Y203.015332 Z2 E3185.914608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.485476 Y202.732239 Z2 E3194.738002 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.412624 Y202.5 Z2 E3199.109098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.485476 Y202.267761 Z2 E3203.480193 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.577017 Y201.984668 Z2 E3212.303587 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.65 Y201.89 Z2 E3221.126982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.722983 Y201.984668 Z2 E3229.950376 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.814524 Y202.267761 Z2 E3238.77377 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.943003 Y202.736553 Z2 E3247.597165 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.126444 Y203.386528 Z2 E3256.420559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.38234 Y204.211428 Z2 E3265.243953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.727489 Y205.203307 Z2 E3274.067348 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.177828 Y206.352614 Z2 E3282.890742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.748281 Y207.648281 Z2 E3291.714137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.452614 Y209.077828 Z2 E3300.537531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.303307 Y210.627489 Z2 E3309.360925 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.311428 Y212.28234 Z2 E3318.18432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.486528 Y214.026444 Z2 E3327.007714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.836553 Y215.843003 Z2 E3335.831108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.367761 Y217.714524 Z2 E3344.654503 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.084668 Y219.622983 Z2 E3353.477897 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.99 Y221.55 Z2 E3362.301291 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.084668 Y223.477017 Z2 E3371.124686 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.367761 Y225.385476 Z2 E3379.94808 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.836553 Y227.256997 Z2 E3388.771474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.486528 Y229.073556 Z2 E3397.594869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.311428 Y230.81766 Z2 E3406.418263 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.303307 Y232.472511 Z2 E3415.241657 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.452614 Y234.022172 Z2 E3424.065052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.748281 Y235.451719 Z2 E3432.888446 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.177828 Y236.747386 Z2 E3441.71184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.727489 Y237.896693 Z2 E3450.535235 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.38234 Y238.888572 Z2 E3459.358629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.126444 Y239.713472 Z2 E3468.182023 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.943003 Y240.363447 Z2 E3477.005418 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.814524 Y240.832239 Z2 E3485.828812 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.722983 Y241.115332 Z2 E3494.652206 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.65 Y241.21 Z2 E3503.475601 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.577017 Y241.115332 Z2 E3512.298995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.485476 Y240.832239 Z2 E3521.12239 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.412624 Y240.6 Z2 E3525.493485 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.485476 Y240.367761 Z2 E3529.86458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.577017 Y240.084668 Z2 E3538.687975 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.65 Y239.99 Z2 E3547.511369 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.722983 Y240.084668 Z2 E3556.334763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.814524 Y240.367761 Z2 E3565.158158 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.943003 Y240.836553 Z2 E3573.981552 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.126444 Y241.486528 Z2 E3582.804946 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.38234 Y242.311428 Z2 E3591.628341 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.727489 Y243.303307 Z2 E3600.451735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.177828 Y244.452614 Z2 E3609.275129 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.748281 Y245.748281 Z2 E3618.098524 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.452614 Y247.177828 Z2 E3626.921918 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.303307 Y248.727489 Z2 E3635.745312 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.311428 Y250.38234 Z2 E3644.568707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.486528 Y252.126444 Z2 E3653.392101 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.836553 Y253.943003 Z2 E3662.215496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.6 Y254.887376 Z2 E3666.667794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.363447 Y253.943003 Z2 E3671.120093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.713472 Y252.126444 Z2 E3679.943488 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.888572 Y250.38234 Z2 E3688.766882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.896693 Y248.727489 Z2 E3697.590276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.747386 Y247.177828 Z2 E3706.413671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.70469 Y247.130721 Z2 E3706.704425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.780267 Y247.564866 Z2 E3712.008921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.856625 Y247.859875 Z2 E3717.112936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.875385 Y248.001825 Z2 E3721.817011 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.839061 Y248.001373 Z2 E3726.224156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.750162 Y247.869176 Z2 E3730.434502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.611203 Y247.615891 Z2 E3734.539108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.424695 Y247.252174 Z2 E3738.614348 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.19315 Y246.788682 Z2 E3742.718454 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.605 Y245.605 Z2 E3751.144224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.788682 Y244.19315 Z2 E3759.569994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.252174 Y243.424695 Z2 E3763.6741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.615891 Y242.611203 Z2 E3767.74934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.869176 Y241.750162 Z2 E3771.853946 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.001373 Y240.839061 Z2 E3776.064292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.001825 Y239.875385 Z2 E3780.471437 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.859875 Y238.856625 Z2 E3785.175512 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.564866 Y237.780267 Z2 E3790.279527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.106143 Y236.643799 Z2 E3795.884323 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.473047 Y235.444709 Z2 E3802.085492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.654922 Y234.180484 Z2 E3808.97216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.641112 Y232.848614 Z2 E3816.627012 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.420959 Y231.446584 Z2 E3825.12697 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.983807 Y229.971884 Z2 E3834.544068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.319 Y228.422 Z2 E3844.946342 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.951602 Y226.738229 Z2 E3854.866082 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.7375 Y224.444203 Z2 E3869.446705 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.721086 Y221.723732 Z2 E3888.023249 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.94675 Y218.760625 Z2 E3909.968086 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.789233 Y217.245523 Z2 E3922.024884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X230.458883 Y215.738689 Z2 E3934.71608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X227.961247 Y214.263101 Z2 E3947.98293 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X225.301875 Y212.841734 Z2 E3961.773093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.486315 Y211.497565 Z2 E3976.041521 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.520117 Y210.253568 Z2 E3990.75143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.408829 Y209.132721 Z2 E4005.875341 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.158 Y208.158 Z2 E4021.396163 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.132721 Y211.408829 Z2 E4036.916985 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.253568 Y214.520117 Z2 E4052.040896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.497565 Y217.486315 Z2 E4066.750805 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.841734 Y220.301875 Z2 E4081.019233 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.263101 Y222.961247 Z2 E4094.809396 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.738689 Y225.458883 Z2 E4108.076246 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.245523 Y227.789233 Z2 E4120.767441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X223.760625 Y229.94675 Z2 E4132.82424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.723732 Y233.721086 Z2 E4154.769076 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X229.444203 Y236.7375 Z2 E4173.34562 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X231.738229 Y238.951602 Z2 E4187.926244 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X233.422 Y240.319 Z2 E4197.845984 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.971884 Y241.983807 Z2 E4208.248257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.446584 Y243.420959 Z2 E4217.665356 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.848614 Y244.641112 Z2 E4226.165313 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.180484 Y245.654922 Z2 E4233.820166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.444709 Y246.473047 Z2 E4240.706833 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.643799 Y247.106143 Z2 E4246.908003 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.70469 Y247.130721 Z2 E4247.208303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.451719 Y245.748281 Z2 E4255.740943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.022172 Y244.452614 Z2 E4264.564337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.472511 Y243.303307 Z2 E4273.387731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.81766 Y242.311428 Z2 E4282.211126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.073556 Y241.486528 Z2 E4291.03452 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.256997 Y240.836553 Z2 E4299.857915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X230.385476 Y240.367761 Z2 E4308.681309 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.477017 Y240.084668 Z2 E4317.504703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.55 Y239.99 Z2 E4326.328098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.622983 Y240.084668 Z2 E4335.151492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.714524 Y240.367761 Z2 E4343.974886 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.843003 Y240.836553 Z2 E4352.798281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.026444 Y241.486528 Z2 E4361.621675 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.28234 Y242.311428 Z2 E4370.445069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.627489 Y243.303307 Z2 E4379.268464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.077828 Y244.452614 Z2 E4388.091858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.648281 Y245.748281 Z2 E4396.915252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.352614 Y247.177828 Z2 E4405.738647 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.203307 Y248.727489 Z2 E4414.562041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.211428 Y250.38234 Z2 E4423.385435 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.386528 Y252.126444 Z2 E4432.20883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.736553 Y253.943003 Z2 E4441.032224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y254.887376 Z2 E4445.484523 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.263447 Y253.943003 Z2 E4449.936822 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.613472 Y252.126444 Z2 E4458.760216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.788572 Y250.38234 Z2 E4467.583611 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.796693 Y248.727489 Z2 E4476.407005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.647386 Y247.177828 Z2 E4485.230399 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.351719 Y245.748281 Z2 E4494.053794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.922172 Y244.452614 Z2 E4502.877188 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.372511 Y243.303307 Z2 E4511.700582 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X197.71766 Y242.311428 Z2 E4520.523977 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.973556 Y241.486528 Z2 E4529.347371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.156997 Y240.836553 Z2 E4538.170765 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.285476 Y240.367761 Z2 E4546.99416 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.377017 Y240.084668 Z2 E4555.817554 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.45 Y239.99 Z2 E4564.640948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.522983 Y240.084668 Z2 E4573.464343 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.614524 Y240.367761 Z2 E4582.287737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.743003 Y240.836553 Z2 E4591.111131 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.926444 Y241.486528 Z2 E4599.934526 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X179.18234 Y242.311428 Z2 E4608.75792 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.527489 Y243.303307 Z2 E4617.581315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.977828 Y244.452614 Z2 E4626.404709 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548281 Y245.748281 Z2 E4635.228103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.252614 Y247.177828 Z2 E4644.051498 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.103307 Y248.727489 Z2 E4652.874892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.111428 Y250.38234 Z2 E4661.698286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.286528 Y252.126444 Z2 E4670.521681 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.636553 Y253.943003 Z2 E4679.345075 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.4 Y254.887376 Z2 E4683.797374 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.163447 Y253.943003 Z2 E4688.249673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.513472 Y252.126444 Z2 E4697.073067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.688572 Y250.38234 Z2 E4705.896461 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.696693 Y248.727489 Z2 E4714.719856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.547386 Y247.177828 Z2 E4723.54325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.251719 Y245.748281 Z2 E4732.366645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.822172 Y244.452614 Z2 E4741.190039 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.272511 Y243.303307 Z2 E4750.013433 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.61766 Y242.311428 Z2 E4758.836828 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.873556 Y241.486528 Z2 E4767.660222 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.056997 Y240.836553 Z2 E4776.483616 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.112624 Y240.6 Z2 E4780.935915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.056997 Y240.363447 Z2 E4785.388214 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.873556 Y239.713472 Z2 E4794.211608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.61766 Y238.888572 Z2 E4803.035003 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.272511 Y237.896693 Z2 E4811.858397 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.822172 Y236.747386 Z2 E4820.681792 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.869279 Y236.70469 Z2 E4820.972546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.435134 Y237.780267 Z2 E4826.277042 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.140125 Y238.856625 Z2 E4831.381057 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.998175 Y239.875385 Z2 E4836.085132 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.998627 Y240.839061 Z2 E4840.492277 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.130824 Y241.750162 Z2 E4844.702622 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.384109 Y242.611203 Z2 E4848.807229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.747826 Y243.424695 Z2 E4852.882469 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.211318 Y244.19315 Z2 E4856.986575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.395 Y245.605 Z2 E4865.412345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.80685 Y246.788682 Z2 E4873.838115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.575305 Y247.252174 Z2 E4877.942221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.388797 Y247.615891 Z2 E4882.017461 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.249838 Y247.869176 Z2 E4886.122067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.160939 Y248.001373 Z2 E4890.332412 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.124615 Y248.001825 Z2 E4894.739558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.143375 Y247.859875 Z2 E4899.443632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.219733 Y247.564866 Z2 E4904.547648 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.356201 Y247.106143 Z2 E4910.152444 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.555291 Y246.473047 Z2 E4916.353613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.819516 Y245.654922 Z2 E4923.24028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.151386 Y244.641112 Z2 E4930.895133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X178.553416 Y243.420959 Z2 E4939.39509 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.028116 Y241.983807 Z2 E4948.812189 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X181.578 Y240.319 Z2 E4959.214463 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X183.261771 Y238.951602 Z2 E4969.134203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X185.555797 Y236.7375 Z2 E4983.714826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.276268 Y233.721086 Z2 E5002.29137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X191.239375 Y229.94675 Z2 E5024.236206 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.754477 Y227.789233 Z2 E5036.293005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.261311 Y225.458883 Z2 E5048.9842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.736899 Y222.961247 Z2 E5062.251051 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X197.158266 Y220.301875 Z2 E5076.041214 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.502435 Y217.486315 Z2 E5090.309642 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.746432 Y214.520117 Z2 E5105.01955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.867279 Y211.408829 Z2 E5120.143462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.842 Y208.158 Z2 E5135.664284 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.591171 Y209.132721 Z2 E5151.185105 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.479883 Y210.253568 Z2 E5166.309017 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.513685 Y211.497565 Z2 E5181.018926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X189.698125 Y212.841734 Z2 E5195.287353 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.038753 Y214.263101 Z2 E5209.077517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.541117 Y215.738689 Z2 E5222.344367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.210767 Y217.245523 Z2 E5235.035562 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.05325 Y218.760625 Z2 E5247.092361 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.278914 Y221.723732 Z2 E5269.037197 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.2625 Y224.444203 Z2 E5287.613741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.048398 Y226.738229 Z2 E5302.194364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.681 Y228.422 Z2 E5312.114104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.016193 Y229.971884 Z2 E5322.516378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.579041 Y231.446584 Z2 E5331.933477 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.358888 Y232.848614 Z2 E5340.433434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.345078 Y234.180484 Z2 E5348.088287 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.526953 Y235.444709 Z2 E5354.974954 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.893857 Y236.643799 Z2 E5361.176123 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.869279 Y236.70469 Z2 E5361.476424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.251719 Y235.451719 Z2 E5370.009064 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.547386 Y234.022172 Z2 E5378.832458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.696693 Y232.472511 Z2 E5387.655852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.688572 Y230.81766 Z2 E5396.479247 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.513472 Y229.073556 Z2 E5405.302641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.163447 Y227.256997 Z2 E5414.126035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.632239 Y225.385476 Z2 E5422.94943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.915332 Y223.477017 Z2 E5431.772824 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.01 Y221.55 Z2 E5440.596218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.915332 Y219.622983 Z2 E5449.419613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.632239 Y217.714524 Z2 E5458.243007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.163447 Y215.843003 Z2 E5467.066401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.513472 Y214.026444 Z2 E5475.889796 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.688572 Y212.28234 Z2 E5484.71319 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.696693 Y210.627489 Z2 E5493.536584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.547386 Y209.077828 Z2 E5502.359979 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.251719 Y207.648281 Z2 E5511.183373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.822172 Y206.352614 Z2 E5520.006767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.272511 Y205.203307 Z2 E5528.830162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.61766 Y204.211428 Z2 E5537.653556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.873556 Y203.386528 Z2 E5546.47695 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.056997 Y202.736553 Z2 E5555.300345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.112624 Y202.5 Z2 E5559.752644 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.056997 Y202.263447 Z2 E5564.204943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.873556 Y201.613472 Z2 E5573.028337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.61766 Y200.788572 Z2 E5581.851731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.272511 Y199.796693 Z2 E5590.675126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.822172 Y198.647386 Z2 E5599.49852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.251719 Y197.351719 Z2 E5608.321914 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.547386 Y195.922172 Z2 E5617.145309 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.696693 Y194.372511 Z2 E5625.968703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.688572 Y192.71766 Z2 E5634.792097 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.513472 Y190.973556 Z2 E5643.615492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.163447 Y189.156997 Z2 E5652.438886 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.632239 Y187.285476 Z2 E5661.26228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.915332 Y185.377017 Z2 E5670.085675 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.01 Y183.45 Z2 E5678.909069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.915332 Y181.522983 Z2 E5687.732464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.632239 Y179.614524 Z2 E5696.555858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.163447 Y177.743003 Z2 E5705.379252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.513472 Y175.926444 Z2 E5714.202647 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.145554 Y175.148548 Z2 E5718.138008 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.681 Y176.578 Z2 E5727.731986 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.048398 Y178.261771 Z2 E5737.651726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.2625 Y180.555797 Z2 E5752.232349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.278914 Y183.276268 Z2 E5770.808893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.05325 Y186.239375 Z2 E5792.753729 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.210767 Y187.754477 Z2 E5804.810528 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.541117 Y189.261311 Z2 E5817.501724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.038753 Y190.736899 Z2 E5830.768574 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X189.698125 Y192.158266 Z2 E5844.558737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.513685 Y193.502435 Z2 E5858.827165 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.479883 Y194.746432 Z2 E5873.537073 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.591171 Y195.867279 Z2 E5888.660985 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.842 Y196.842 Z2 E5904.181807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.867279 Y193.591171 Z2 E5919.702628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.746432 Y190.479883 Z2 E5934.82654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.502435 Y187.513685 Z2 E5949.536449 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X197.158266 Y184.698125 Z2 E5963.804876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.736899 Y182.038753 Z2 E5977.59504 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.261311 Y179.541117 Z2 E5990.86189 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.754477 Y177.210767 Z2 E6003.553085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X191.239375 Y175.05325 Z2 E6015.609884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.276268 Y171.278914 Z2 E6037.55472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X185.555797 Y168.2625 Z2 E6056.131264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X183.261771 Y166.048398 Z2 E6070.711888 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X181.578 Y164.681 Z2 E6080.631627 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.028116 Y163.016193 Z2 E6091.033901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X178.553416 Y161.579041 Z2 E6100.451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.151386 Y160.358888 Z2 E6108.950957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.819516 Y159.345078 Z2 E6116.60581 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.555291 Y158.526953 Z2 E6123.492477 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.356201 Y157.893857 Z2 E6129.693646 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.219733 Y157.435134 Z2 E6135.298442 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.143375 Y157.140125 Z2 E6140.402458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.124615 Y156.998175 Z2 E6145.106533 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.160939 Y156.998627 Z2 E6149.513678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.249838 Y157.130824 Z2 E6153.724023 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.388797 Y157.384109 Z2 E6157.82863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.575305 Y157.747826 Z2 E6161.903869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.80685 Y158.211318 Z2 E6166.007976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.395 Y159.395 Z2 E6174.433745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.211318 Y160.80685 Z2 E6182.859515 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.747826 Y161.575305 Z2 E6186.963622 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.384109 Y162.388797 Z2 E6191.038861 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.130824 Y163.249838 Z2 E6195.143468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.998627 Y164.160939 Z2 E6199.353813 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.998175 Y165.124615 Z2 E6203.760958 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.140125 Y166.143375 Z2 E6208.465033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.435134 Y167.219733 Z2 E6213.569048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.893857 Y168.356201 Z2 E6219.173845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.526953 Y169.555291 Z2 E6225.375014 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.345078 Y170.819516 Z2 E6232.261681 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.358888 Y172.151386 Z2 E6239.916534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.579041 Y173.553416 Z2 E6248.416491 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.016193 Y175.028116 Z2 E6257.83359 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.145554 Y175.148548 Z2 E6258.641886 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.688572 Y174.18234 Z2 E6263.529919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.696693 Y172.527489 Z2 E6272.353313 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.547386 Y170.977828 Z2 E6281.176707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.251719 Y169.548281 Z2 E6290.000102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.822172 Y168.252614 Z2 E6298.823496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.272511 Y167.103307 Z2 E6307.64689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.61766 Y166.111428 Z2 E6316.470285 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.873556 Y165.286528 Z2 E6325.293679 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.056997 Y164.636553 Z2 E6334.117073 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.112624 Y164.4 Z2 E6338.569372 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.056997 Y164.163447 Z2 E6343.021671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.873556 Y163.513472 Z2 E6351.845066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.61766 Y162.688572 Z2 E6360.66846 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.272511 Y161.696693 Z2 E6369.491854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.822172 Y160.547386 Z2 E6378.315249 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.251719 Y159.251719 Z2 E6387.138643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.547386 Y157.822172 Z2 E6395.962037 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.696693 Y156.272511 Z2 E6404.785432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.688572 Y154.61766 Z2 E6413.608826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.513472 Y152.873556 Z2 E6422.43222 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.163447 Y151.056997 Z2 E6431.255615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.632239 Y149.185476 Z2 E6440.079009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.915332 Y147.277017 Z2 E6448.902403 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.01 Y145.35 Z2 E6457.725798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.915332 Y143.422983 Z2 E6466.549192 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.632239 Y141.514524 Z2 E6475.372586 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.4 Y140.587376 Z2 E6479.743682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.167761 Y141.514524 Z2 E6484.114777 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.884668 Y143.422983 Z2 E6492.938172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.79 Y145.35 Z2 E6501.761566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.884668 Y147.277017 Z2 E6510.58496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.167761 Y149.185476 Z2 E6519.408355 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.636553 Y151.056997 Z2 E6528.231749 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.286528 Y152.873556 Z2 E6537.055143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.111428 Y154.61766 Z2 E6545.878538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.103307 Y156.272511 Z2 E6554.701932 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.252614 Y157.822172 Z2 E6563.525326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548281 Y159.251719 Z2 E6572.348721 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.977828 Y160.547386 Z2 E6581.172115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.527489 Y161.696693 Z2 E6589.995509 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X179.18234 Y162.688572 Z2 E6598.818904 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.926444 Y163.513472 Z2 E6607.642298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.743003 Y164.163447 Z2 E6616.465692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.614524 Y164.632239 Z2 E6625.289087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.522983 Y164.915332 Z2 E6634.112481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.45 Y165.01 Z2 E6642.935875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.377017 Y164.915332 Z2 E6651.75927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.285476 Y164.632239 Z2 E6660.582664 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.156997 Y164.163447 Z2 E6669.406058 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.973556 Y163.513472 Z2 E6678.229453 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X197.71766 Y162.688572 Z2 E6687.052847 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.372511 Y161.696693 Z2 E6695.876242 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.922172 Y160.547386 Z2 E6704.699636 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.351719 Y159.251719 Z2 E6713.52303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.647386 Y157.822172 Z2 E6722.346425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.796693 Y156.272511 Z2 E6731.169819 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.788572 Y154.61766 Z2 E6739.993213 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.613472 Y152.873556 Z2 E6748.816608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.263447 Y151.056997 Z2 E6757.640002 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.732239 Y149.185476 Z2 E6766.463396 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.015332 Y147.277017 Z2 E6775.286791 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.11 Y145.35 Z2 E6784.110185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.015332 Y143.422983 Z2 E6792.933579 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.732239 Y141.514524 Z2 E6801.756974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y140.587376 Z2 E6806.128069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.267761 Y141.514524 Z2 E6810.499164 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.984668 Y143.422983 Z2 E6819.322559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.89 Y145.35 Z2 E6828.145953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.984668 Y147.277017 Z2 E6836.969348 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.267761 Y149.185476 Z2 E6845.792742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.736553 Y151.056997 Z2 E6854.616136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.386528 Y152.873556 Z2 E6863.439531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.211428 Y154.61766 Z2 E6872.262925 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.203307 Y156.272511 Z2 E6881.086319 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.352614 Y157.822172 Z2 E6889.909714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.648281 Y159.251719 Z2 E6898.733108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.077828 Y160.547386 Z2 E6907.556502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.627489 Y161.696693 Z2 E6916.379897 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.28234 Y162.688572 Z2 E6925.203291 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.026444 Y163.513472 Z2 E6934.026685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.843003 Y164.163447 Z2 E6942.85008 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.714524 Y164.632239 Z2 E6951.673474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.622983 Y164.915332 Z2 E6960.496868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.55 Y165.01 Z2 E6969.320263 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.477017 Y164.915332 Z2 E6978.143657 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X230.385476 Y164.632239 Z2 E6986.967051 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.256997 Y164.163447 Z2 E6995.790446 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.073556 Y163.513472 Z2 E7004.61384 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.851452 Y163.145554 Z2 E7008.549202 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X233.422 Y164.681 Z2 E7018.143179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X231.738229 Y166.048398 Z2 E7028.062919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X229.444203 Y168.2625 Z2 E7042.643542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.723732 Y171.278914 Z2 E7061.220087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X223.760625 Y175.05325 Z2 E7083.164923 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.245523 Y177.210767 Z2 E7095.221722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.738689 Y179.541117 Z2 E7107.912917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.263101 Y182.038753 Z2 E7121.179767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.841734 Y184.698125 Z2 E7134.96993 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.497565 Y187.513685 Z2 E7149.238358 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.253568 Y190.479883 Z2 E7163.948267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.132721 Y193.591171 Z2 E7179.072178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.158 Y196.842 Z2 E7194.593 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.888154 Y197.111846 Z2 E7196.338252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.733445 Y196.164202 Z2 E7203.169715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.416048 Y195.460038 Z2 E7210.001178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.986588 Y195.026416 Z2 E7216.832641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y194.88 Z2 E7223.664103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y194.499 Z2 E7225.406519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.774106 Y192.714788 Z2 E7235.433099 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.888305 Y190.927807 Z2 E7245.063866 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.852351 Y189.150097 Z2 E7254.312316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.676 Y187.393703 Z2 E7263.184126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.369009 Y185.670666 Z2 E7271.677509 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.941133 Y183.993029 Z2 E7279.783673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.76175 Y180.822125 Z2 E7294.762818 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.215898 Y177.97733 Z2 E7307.93757 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.381625 Y175.554984 Z2 E7319.041504 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.336977 Y173.651428 Z2 E7327.749374 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.16 Y172.363 Z2 E7333.697026 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.224358 Y171.005663 Z2 E7339.911466 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.101531 Y168.669036 Z2 E7350.612242 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.923469 Y167.678625 Z2 E7355.214279 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.356855 Y166.025805 Z2 E7363.2049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.977427 Y165.352274 Z2 E7366.740273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.54 Y164.77325 Z2 E7370.059003 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.049135 Y164.283171 Z2 E7373.23117 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.925339 Y163.547606 Z2 E7379.37362 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.301531 Y163.291 Z2 E7382.458402 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.952902 Y162.972336 Z2 E7388.795881 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y162.876 Z2 E7395.454984 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.047098 Y162.972336 Z2 E7402.114087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.698469 Y163.291 Z2 E7408.451566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.074661 Y163.547606 Z2 E7411.536348 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.950865 Y164.283171 Z2 E7417.678798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.46 Y164.77325 Z2 E7420.850965 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.022573 Y165.352274 Z2 E7424.169695 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.643145 Y166.025805 Z2 E7427.705068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.076531 Y167.678625 Z2 E7435.695689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.898469 Y168.669036 Z2 E7440.297725 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.775642 Y171.005663 Z2 E7450.998502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.84 Y172.363 Z2 E7457.212942 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.663023 Y173.651428 Z2 E7463.160594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.618375 Y175.554984 Z2 E7471.868464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.784102 Y177.97733 Z2 E7482.972398 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.23825 Y180.822125 Z2 E7496.14715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.058867 Y183.993029 Z2 E7511.126295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.630991 Y185.670666 Z2 E7519.232459 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.324 Y187.393703 Z2 E7527.725842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.147649 Y189.150097 Z2 E7536.597652 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.111695 Y190.927807 Z2 E7545.846102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.225894 Y192.714788 Z2 E7555.476868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y194.499 Z2 E7565.503449 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y194.88 Z2 E7567.245865 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.013412 Y195.026416 Z2 E7574.077327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.583952 Y195.460038 Z2 E7580.90879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.266555 Y196.164202 Z2 E7587.740253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.111846 Y197.111846 Z2 E7594.571715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.164202 Y198.266555 Z2 E7601.403178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.460038 Y199.583952 Z2 E7608.234641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.026416 Y201.013412 Z2 E7615.066103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.88 Y202.5 Z2 E7621.897566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.499 Y202.5 Z2 E7623.639982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X197.714788 Y201.225894 Z2 E7633.666562 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.927807 Y200.111695 Z2 E7643.297329 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.150097 Y199.147649 Z2 E7652.545779 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.393703 Y198.324 Z2 E7661.417589 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.670666 Y197.630991 Z2 E7669.910972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.993029 Y197.058867 Z2 E7678.017136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X185.822125 Y196.23825 Z2 E7692.996281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.97733 Y195.784102 Z2 E7706.171033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.554984 Y195.618375 Z2 E7717.274967 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X178.651428 Y195.663023 Z2 E7725.982837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.363 Y195.84 Z2 E7731.930489 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.005663 Y195.775642 Z2 E7738.144929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.669036 Y195.898469 Z2 E7748.845705 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.678625 Y196.076531 Z2 E7753.447742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.025805 Y196.643145 Z2 E7761.438363 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.352274 Y197.022573 Z2 E7764.973735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.77325 Y197.46 Z2 E7768.292466 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.283171 Y197.950865 Z2 E7771.464633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.547606 Y199.074661 Z2 E7777.607083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.291 Y199.698469 Z2 E7780.691865 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.972336 Y201.047098 Z2 E7787.029344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.876 Y202.5 Z2 E7793.688447 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.972336 Y203.952902 Z2 E7800.34755 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.291 Y205.301531 Z2 E7806.685029 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.547606 Y205.925339 Z2 E7809.769811 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.283171 Y207.049135 Z2 E7815.912261 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.77325 Y207.54 Z2 E7819.084427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.352274 Y207.977427 Z2 E7822.403158 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.025805 Y208.356855 Z2 E7825.938531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.678625 Y208.923469 Z2 E7833.929152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.669036 Y209.101531 Z2 E7838.531188 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.005663 Y209.224358 Z2 E7849.231964 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.363 Y209.16 Z2 E7855.446405 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X178.651428 Y209.336977 Z2 E7861.394057 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.554984 Y209.381625 Z2 E7870.101927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.97733 Y209.215898 Z2 E7881.205861 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X185.822125 Y208.76175 Z2 E7894.380613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.993029 Y207.941133 Z2 E7909.359758 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.670666 Y207.369009 Z2 E7917.465922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.393703 Y206.676 Z2 E7925.959305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.150097 Y205.852351 Z2 E7934.831115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.927807 Y204.888305 Z2 E7944.079565 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X197.714788 Y203.774106 Z2 E7953.710331 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.499 Y202.5 Z2 E7963.736912 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.88 Y202.5 Z2 E7965.479328 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.026416 Y203.986588 Z2 E7972.31079 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.460038 Y205.416048 Z2 E7979.142253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.164202 Y206.733445 Z2 E7985.973716 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.111846 Y207.888154 Z2 E7992.805178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.266555 Y208.835798 Z2 E7999.636641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.583952 Y209.539962 Z2 E8006.468104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.013412 Y209.973584 Z2 E8013.299566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y210.12 Z2 E8020.131029 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y210.501 Z2 E8021.873444 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.225894 Y212.285212 Z2 E8031.900025 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.111695 Y214.072193 Z2 E8041.530792 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.147649 Y215.849903 Z2 E8050.779242 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.324 Y217.606297 Z2 E8059.651052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.630991 Y219.329334 Z2 E8068.144434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.058867 Y221.006971 Z2 E8076.250599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.23825 Y224.177875 Z2 E8091.229744 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.784102 Y227.02267 Z2 E8104.404496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.618375 Y229.445016 Z2 E8115.508429 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.663023 Y231.348572 Z2 E8124.2163 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.84 Y232.637 Z2 E8130.163952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.775642 Y233.994337 Z2 E8136.378392 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.898469 Y236.330964 Z2 E8147.079168 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.076531 Y237.321375 Z2 E8151.681204 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.643145 Y238.974195 Z2 E8159.671826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.022573 Y239.647726 Z2 E8163.207198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.46 Y240.22675 Z2 E8166.525929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.950865 Y240.716829 Z2 E8169.698096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.074661 Y241.452394 Z2 E8175.840546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.698469 Y241.709 Z2 E8178.925328 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.047098 Y242.027664 Z2 E8185.262807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y242.124 Z2 E8191.92191 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.952902 Y242.027664 Z2 E8198.581013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.301531 Y241.709 Z2 E8204.918492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.925339 Y241.452394 Z2 E8208.003274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.049135 Y240.716829 Z2 E8214.145724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.54 Y240.22675 Z2 E8217.31789 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.977427 Y239.647726 Z2 E8220.636621 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.356855 Y238.974195 Z2 E8224.171994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.923469 Y237.321375 Z2 E8232.162615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.101531 Y236.330964 Z2 E8236.764651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.224358 Y233.994337 Z2 E8247.465427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.16 Y232.637 Z2 E8253.679868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.336977 Y231.348572 Z2 E8259.62752 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.381625 Y229.445016 Z2 E8268.33539 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.215898 Y227.02267 Z2 E8279.439324 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.76175 Y224.177875 Z2 E8292.614076 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.941133 Y221.006971 Z2 E8307.593221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.369009 Y219.329334 Z2 E8315.699385 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.676 Y217.606297 Z2 E8324.192768 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.852351 Y215.849903 Z2 E8333.064578 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.888305 Y214.072193 Z2 E8342.313028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.774106 Y212.285212 Z2 E8351.943794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y210.501 Z2 E8361.970375 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y210.12 Z2 E8363.712791 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.986588 Y209.973584 Z2 E8370.544253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.416048 Y209.539962 Z2 E8377.375716 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.733445 Y208.835798 Z2 E8384.207179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.888154 Y207.888154 Z2 E8391.038641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.835798 Y206.733445 Z2 E8397.870104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.539962 Y205.416048 Z2 E8404.701567 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.973584 Y203.986588 Z2 E8411.533029 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.12 Y202.5 Z2 E8418.364492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.501 Y202.5 Z2 E8420.106907 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.285212 Y203.774106 Z2 E8430.133488 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.072193 Y204.888305 Z2 E8439.764255 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.849903 Y205.852351 Z2 E8449.012705 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.606297 Y206.676 Z2 E8457.884515 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.329334 Y207.369009 Z2 E8466.377897 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.006971 Y207.941133 Z2 E8474.484062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X229.177875 Y208.76175 Z2 E8489.463207 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.02267 Y209.215898 Z2 E8502.637959 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.445016 Y209.381625 Z2 E8513.741892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.348572 Y209.336977 Z2 E8522.449763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.637 Y209.16 Z2 E8528.397415 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.994337 Y209.224358 Z2 E8534.611855 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.330964 Y209.101531 Z2 E8545.312631 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.321375 Y208.923469 Z2 E8549.914667 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.974195 Y208.356855 Z2 E8557.905289 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.647726 Y207.977427 Z2 E8561.440661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.22675 Y207.54 Z2 E8564.759392 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.716829 Y207.049135 Z2 E8567.931559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.452394 Y205.925339 Z2 E8574.074009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.709 Y205.301531 Z2 E8577.158791 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.027664 Y203.952902 Z2 E8583.49627 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.124 Y202.5 Z2 E8590.155373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.027664 Y201.047098 Z2 E8596.814476 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.709 Y199.698469 Z2 E8603.151955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.452394 Y199.074661 Z2 E8606.236737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.716829 Y197.950865 Z2 E8612.379187 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.22675 Y197.46 Z2 E8615.551353 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.647726 Y197.022573 Z2 E8618.870084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.974195 Y196.643145 Z2 E8622.405457 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.321375 Y196.076531 Z2 E8630.396078 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.330964 Y195.898469 Z2 E8634.998114 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.994337 Y195.775642 Z2 E8645.69889 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.637 Y195.84 Z2 E8651.91333 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.348572 Y195.663023 Z2 E8657.860983 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.445016 Y195.618375 Z2 E8666.568853 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.02267 Y195.784102 Z2 E8677.672787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X229.177875 Y196.23825 Z2 E8690.847539 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.006971 Y197.058867 Z2 E8705.826684 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.329334 Y197.630991 Z2 E8713.932848 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.606297 Y198.324 Z2 E8722.426231 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.849903 Y199.147649 Z2 E8731.298041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.072193 Y200.111695 Z2 E8740.546491 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.285212 Y201.225894 Z2 E8750.177257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.501 Y202.5 Z2 E8760.203838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.12 Y202.5 Z2 E8761.946254 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.973584 Y201.013412 Z2 E8768.777716 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.539962 Y199.583952 Z2 E8775.609179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.835798 Y198.266555 Z2 E8782.440642 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.888154 Y197.111846 Z2 E8789.272104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.158 Y196.842 Z2 E8791.017357 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.408829 Y195.867279 Z2 E8806.538178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.520117 Y194.746432 Z2 E8821.66209 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.486315 Y193.502435 Z2 E8836.371999 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X225.301875 Y192.158266 Z2 E8850.640426 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X227.961247 Y190.736899 Z2 E8864.43059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X230.458883 Y189.261311 Z2 E8877.69744 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.789233 Y187.754477 Z2 E8890.388635 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.94675 Y186.239375 Z2 E8902.445434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.721086 Y183.276268 Z2 E8924.39027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.7375 Y180.555797 Z2 E8942.966814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.951602 Y178.261771 Z2 E8957.547438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.319 Y176.578 Z2 E8967.467177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.983807 Y175.028116 Z2 E8977.869451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.420959 Y173.553416 Z2 E8987.28655 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.641112 Y172.151386 Z2 E8995.786507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.654922 Y170.819516 Z2 E9003.44136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.473047 Y169.555291 Z2 E9010.328027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.106143 Y168.356201 Z2 E9016.529196 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.564866 Y167.219733 Z2 E9022.133992 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.859875 Y166.143375 Z2 E9027.238008 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.001825 Y165.124615 Z2 E9031.942083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.001373 Y164.160939 Z2 E9036.349228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.869176 Y163.249838 Z2 E9040.559573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.615891 Y162.388797 Z2 E9044.66418 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.252174 Y161.575305 Z2 E9048.739419 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.788682 Y160.80685 Z2 E9052.843526 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.605 Y159.395 Z2 E9061.269295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.19315 Y158.211318 Z2 E9069.695065 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.424695 Y157.747826 Z2 E9073.799172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.611203 Y157.384109 Z2 E9077.874411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.750162 Y157.130824 Z2 E9081.979018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.839061 Y156.998627 Z2 E9086.189363 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.875385 Y156.998175 Z2 E9090.596508 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.856625 Y157.140125 Z2 E9095.300583 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.780267 Y157.435134 Z2 E9100.404598 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.643799 Y157.893857 Z2 E9106.009395 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.444709 Y158.526953 Z2 E9112.210564 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.180484 Y159.345078 Z2 E9119.097231 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.848614 Y160.358888 Z2 E9126.752084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.446584 Y161.579041 Z2 E9135.252041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.971884 Y163.016193 Z2 E9144.66914 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.851452 Y163.145554 Z2 E9145.477436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.81766 Y162.688572 Z2 E9150.365469 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.472511 Y161.696693 Z2 E9159.188863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.022172 Y160.547386 Z2 E9168.012257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.451719 Y159.251719 Z2 E9176.835652 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.747386 Y157.822172 Z2 E9185.659046 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.896693 Y156.272511 Z2 E9194.48244 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.888572 Y154.61766 Z2 E9203.305835 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.713472 Y152.873556 Z2 E9212.129229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.363447 Y151.056997 Z2 E9220.952623 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.832239 Y149.185476 Z2 E9229.776018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.115332 Y147.277017 Z2 E9238.599412 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.21 Y145.35 Z2 E9247.422806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.115332 Y143.422983 Z2 E9256.246201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.832239 Y141.514524 Z2 E9265.069595 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.6 Y140.587376 Z2 E9269.44069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.367761 Y141.514524 Z2 E9273.811786 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.084668 Y143.422983 Z2 E9282.63518 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.99 Y145.35 Z2 E9291.458575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.084668 Y147.277017 Z2 E9300.281969 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.367761 Y149.185476 Z2 E9309.105363 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.836553 Y151.056997 Z2 E9317.928758 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.486528 Y152.873556 Z2 E9326.752152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.311428 Y154.61766 Z2 E9335.575546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.303307 Y156.272511 Z2 E9344.398941 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.452614 Y157.822172 Z2 E9353.222335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.748281 Y159.251719 Z2 E9362.045729 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.177828 Y160.547386 Z2 E9370.869124 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.727489 Y161.696693 Z2 E9379.692518 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.38234 Y162.688572 Z2 E9388.515912 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.126444 Y163.513472 Z2 E9397.339307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.943003 Y164.163447 Z2 E9406.162701 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.814524 Y164.632239 Z2 E9414.986095 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.722983 Y164.915332 Z2 E9423.80949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.65 Y165.01 Z2 E9432.632884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.577017 Y164.915332 Z2 E9441.456278 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.485476 Y164.632239 Z2 E9450.279673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.356997 Y164.163447 Z2 E9459.103067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.173556 Y163.513472 Z2 E9467.926461 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.91766 Y162.688572 Z2 E9476.749856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.572511 Y161.696693 Z2 E9485.57325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.122172 Y160.547386 Z2 E9494.396645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.551719 Y159.251719 Z2 E9503.220039 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.847386 Y157.822172 Z2 E9512.043433 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.996693 Y156.272511 Z2 E9520.866828 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.988572 Y154.61766 Z2 E9529.690222 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X282.813472 Y152.873556 Z2 E9538.513616 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.463447 Y151.056997 Z2 E9547.337011 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.932239 Y149.185476 Z2 E9556.160405 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.215332 Y147.277017 Z2 E9564.983799 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.31 Y145.35 Z2 E9573.807194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X284.215332 Y143.422983 Z2 E9582.630588 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.932239 Y141.514524 Z2 E9591.453982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X283.463447 Y139.643003 Z2 E9600.277377 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X282.813472 Y137.826444 Z2 E9609.100771 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.988572 Y136.08234 Z2 E9617.924165 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.996693 Y134.427489 Z2 E9626.74756 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.847386 Y132.877828 Z2 E9635.570954 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.551719 Y131.448281 Z2 E9644.394348 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.122172 Y130.152614 Z2 E9653.217743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.572511 Y129.003307 Z2 E9662.041137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.91766 Y128.011428 Z2 E9670.864531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.173556 Y127.186528 Z2 E9679.687926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.356997 Y126.536553 Z2 E9688.51132 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.485476 Y126.067761 Z2 E9697.334714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.577017 Y125.784668 Z2 E9706.158109 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.65 Y125.69 Z2 E9714.981503 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.722983 Y125.784668 Z2 E9723.804898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.814524 Y126.067761 Z2 E9732.628292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.943003 Y126.536553 Z2 E9741.451686 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.126444 Y127.186528 Z2 E9750.275081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.38234 Y128.011428 Z2 E9759.098475 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.727489 Y129.003307 Z2 E9767.921869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.177828 Y130.152614 Z2 E9776.745264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.748281 Y131.448281 Z2 E9785.568658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.452614 Y132.877828 Z2 E9794.392052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.303307 Y134.427489 Z2 E9803.215447 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.311428 Y136.08234 Z2 E9812.038841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.486528 Y137.826444 Z2 E9820.862235 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.836553 Y139.643003 Z2 E9829.68563 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.6 Y140.587376 Z2 E9834.137929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.363447 Y139.643003 Z2 E9838.590228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.713472 Y137.826444 Z2 E9847.413622 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.888572 Y136.08234 Z2 E9856.237016 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.896693 Y134.427489 Z2 E9865.060411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.747386 Y132.877828 Z2 E9873.883805 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.451719 Y131.448281 Z2 E9882.707199 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.022172 Y130.152614 Z2 E9891.530594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.472511 Y129.003307 Z2 E9900.353988 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.81766 Y128.011428 Z2 E9909.177382 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.073556 Y127.186528 Z2 E9918.000777 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.256997 Y126.536553 Z2 E9926.824171 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X230.385476 Y126.067761 Z2 E9935.647565 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.477017 Y125.784668 Z2 E9944.47096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.55 Y125.69 Z2 E9953.294354 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.622983 Y125.784668 Z2 E9962.117748 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.714524 Y126.067761 Z2 E9970.941143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.843003 Y126.536553 Z2 E9979.764537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.026444 Y127.186528 Z2 E9988.587931 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.28234 Y128.011428 Z2 E9997.411326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.627489 Y129.003307 Z2 E10006.23472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.077828 Y130.152614 Z2 E10015.058114 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.648281 Y131.448281 Z2 E10023.881509 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.352614 Y132.877828 Z2 E10032.704903 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.203307 Y134.427489 Z2 E10041.528297 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.211428 Y136.08234 Z2 E10050.351692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.386528 Y137.826444 Z2 E10059.175086 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.736553 Y139.643003 Z2 E10067.998481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.5 Y140.587376 Z2 E10072.450779 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.263447 Y139.643003 Z2 E10076.903078 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.613472 Y137.826444 Z2 E10085.726473 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.788572 Y136.08234 Z2 E10094.549867 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.796693 Y134.427489 Z2 E10103.373261 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.647386 Y132.877828 Z2 E10112.196656 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.351719 Y131.448281 Z2 E10121.02005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.922172 Y130.152614 Z2 E10129.843444 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.372511 Y129.003307 Z2 E10138.666839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X197.71766 Y128.011428 Z2 E10147.490233 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.973556 Y127.186528 Z2 E10156.313628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.156997 Y126.536553 Z2 E10165.137022 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.285476 Y126.067761 Z2 E10173.960416 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.377017 Y125.784668 Z2 E10182.783811 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.45 Y125.69 Z2 E10191.607205 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.522983 Y125.784668 Z2 E10200.430599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.614524 Y126.067761 Z2 E10209.253994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.743003 Y126.536553 Z2 E10218.077388 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.926444 Y127.186528 Z2 E10226.900782 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X179.18234 Y128.011428 Z2 E10235.724177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.527489 Y129.003307 Z2 E10244.547571 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.977828 Y130.152614 Z2 E10253.370965 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548281 Y131.448281 Z2 E10262.19436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.252614 Y132.877828 Z2 E10271.017754 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.103307 Y134.427489 Z2 E10279.841148 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.111428 Y136.08234 Z2 E10288.664543 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.286528 Y137.826444 Z2 E10297.487937 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.636553 Y139.643003 Z2 E10306.311331 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.4 Y140.587376 Z2 E10310.76363 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.163447 Y139.643003 Z2 E10315.215929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.513472 Y137.826444 Z2 E10324.039324 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.688572 Y136.08234 Z2 E10332.862718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.696693 Y134.427489 Z2 E10341.686112 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.547386 Y132.877828 Z2 E10350.509507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.251719 Y131.448281 Z2 E10359.332901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.822172 Y130.152614 Z2 E10368.156295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X161.272511 Y129.003307 Z2 E10376.97969 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.61766 Y128.011428 Z2 E10385.803084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.873556 Y127.186528 Z2 E10394.626478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.056997 Y126.536553 Z2 E10403.449873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.185476 Y126.067761 Z2 E10412.273267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.277017 Y125.784668 Z2 E10421.096661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.35 Y125.69 Z2 E10429.920056 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.422983 Y125.784668 Z2 E10438.74345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.514524 Y126.067761 Z2 E10447.566844 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.643003 Y126.536553 Z2 E10456.390239 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.826444 Y127.186528 Z2 E10465.213633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.08234 Y128.011428 Z2 E10474.037028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.40643 Y128.416553 Z2 E10477.640868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.427489 Y129.003307 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X137.877828 Y130.152614 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X136.448281 Y131.448281 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
; CLAYLINE_MARKER page=0 layer=1 text=layer 1 page_id=page-0-rings-grid-base page_name=rings-grid-base z_mode=calibrated
G0 X136.448281 Y131.448281 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0000 note=vertical layer transition
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0000
G1 X137.559707 Y130.440942 Z4 E10477.952681 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X137.877828 Y130.152614 Z4 E10478.156726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X138.737789 Y129.514824 Z4 E10478.888123 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X139.427489 Y129.003307 Z4 E10479.704302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X139.977566 Y128.673604 Z4 E10480.447192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X141.08234 Y128.011428 Z4 E10482.283596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X141.273965 Y127.920796 Z4 E10482.629888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X142.629949 Y127.279463 Z4 E10485.436212 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X142.826444 Y127.186528 Z4 E10485.894606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X144.034102 Y126.754421 Z4 E10488.866163 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X144.643003 Y126.536553 Z4 E10490.537334 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X145.470726 Y126.329219 Z4 E10492.919742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X146.514524 Y126.067761 Z4 E10496.21178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X146.93389 Y126.005554 Z4 E10497.596949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X148.417655 Y125.785459 Z4 E10502.897783 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X148.422983 Y125.784668 Z4 E10502.917942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X149.915796 Y125.711331 Z4 E10508.822244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X150.35 Y125.69 Z4 E10510.629632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X152.277017 Y125.784668 Z4 E10518.650899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X154.185476 Y126.067761 Z4 E10526.672167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X156.056997 Y126.536553 Z4 E10534.693435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X157.873556 Y127.186528 Z4 E10542.714702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X159.61766 Y128.011428 Z4 E10550.73597 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.272511 Y129.003307 Z4 E10558.757237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.822172 Y130.152614 Z4 E10566.778505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.251719 Y131.448281 Z4 E10574.799773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.547386 Y132.877828 Z4 E10582.82104 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.696693 Y134.427489 Z4 E10590.842308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.688572 Y136.08234 Z4 E10598.863575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.513472 Y137.826444 Z4 E10606.884843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.163447 Y139.643003 Z4 E10614.90611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.4 Y140.587376 Z4 E10618.953655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.636553 Y139.643003 Z4 E10623.001199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.286528 Y137.826444 Z4 E10631.022467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.111428 Y136.08234 Z4 E10639.043735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X172.103307 Y134.427489 Z4 E10647.065002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.252614 Y132.877828 Z4 E10655.08627 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X174.548281 Y131.448281 Z4 E10663.107537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X175.977828 Y130.152614 Z4 E10671.128805 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X177.527489 Y129.003307 Z4 E10679.150073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X179.18234 Y128.011428 Z4 E10687.17134 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.926444 Y127.186528 Z4 E10695.192608 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X182.743003 Y126.536553 Z4 E10703.213875 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X184.614524 Y126.067761 Z4 E10711.235143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X186.522983 Y125.784668 Z4 E10719.25641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X188.45 Y125.69 Z4 E10727.277678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X190.377017 Y125.784668 Z4 E10735.298946 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.285476 Y126.067761 Z4 E10743.320213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X194.156997 Y126.536553 Z4 E10751.341481 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.973556 Y127.186528 Z4 E10759.362748 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X197.71766 Y128.011428 Z4 E10767.384016 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.372511 Y129.003307 Z4 E10775.405284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.922172 Y130.152614 Z4 E10783.426551 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.351719 Y131.448281 Z4 E10791.447819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X203.647386 Y132.877828 Z4 E10799.469086 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.796693 Y134.427489 Z4 E10807.490354 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X205.788572 Y136.08234 Z4 E10815.511622 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.613472 Y137.826444 Z4 E10823.532889 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.263447 Y139.643003 Z4 E10831.554157 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y140.587376 Z4 E10835.601701 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.736553 Y139.643003 Z4 E10839.649246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.386528 Y137.826444 Z4 E10847.670513 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X209.211428 Y136.08234 Z4 E10855.691781 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.203307 Y134.427489 Z4 E10863.713048 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X211.352614 Y132.877828 Z4 E10871.734316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.648281 Y131.448281 Z4 E10879.755584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.077828 Y130.152614 Z4 E10887.776851 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.627489 Y129.003307 Z4 E10895.798119 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X217.28234 Y128.011428 Z4 E10903.819386 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.026444 Y127.186528 Z4 E10911.840654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X220.843003 Y126.536553 Z4 E10919.861922 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.714524 Y126.067761 Z4 E10927.883189 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.622983 Y125.784668 Z4 E10935.904457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X226.55 Y125.69 Z4 E10943.925724 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X228.477017 Y125.784668 Z4 E10951.946992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X230.385476 Y126.067761 Z4 E10959.968259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X232.256997 Y126.536553 Z4 E10967.989527 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.073556 Y127.186528 Z4 E10976.010795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X235.81766 Y128.011428 Z4 E10984.032062 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.472511 Y129.003307 Z4 E10992.05333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X239.022172 Y130.152614 Z4 E11000.074597 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X240.451719 Y131.448281 Z4 E11008.095865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.747386 Y132.877828 Z4 E11016.117133 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.896693 Y134.427489 Z4 E11024.1384 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.888572 Y136.08234 Z4 E11032.159668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.713472 Y137.826444 Z4 E11040.180935 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.363447 Y139.643003 Z4 E11048.202203 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.6 Y140.587376 Z4 E11052.249747 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.836553 Y139.643003 Z4 E11056.297292 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.486528 Y137.826444 Z4 E11064.31856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.311428 Y136.08234 Z4 E11072.339827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.303307 Y134.427489 Z4 E11080.361095 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.452614 Y132.877828 Z4 E11088.382362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.748281 Y131.448281 Z4 E11096.40363 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.177828 Y130.152614 Z4 E11104.424897 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.727489 Y129.003307 Z4 E11112.446165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.38234 Y128.011428 Z4 E11120.467433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X257.126444 Y127.186528 Z4 E11128.4887 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.943003 Y126.536553 Z4 E11136.509968 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.814524 Y126.067761 Z4 E11144.531235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X262.722983 Y125.784668 Z4 E11152.552503 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X264.65 Y125.69 Z4 E11160.573771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X266.577017 Y125.784668 Z4 E11168.595038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X268.485476 Y126.067761 Z4 E11176.616306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X270.356997 Y126.536553 Z4 E11184.637573 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.173556 Y127.186528 Z4 E11192.658841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X273.91766 Y128.011428 Z4 E11200.680109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.572511 Y129.003307 Z4 E11208.701376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.122172 Y130.152614 Z4 E11216.722644 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X278.551719 Y131.448281 Z4 E11224.743911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X279.847386 Y132.877828 Z4 E11232.765179 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X280.996693 Y134.427489 Z4 E11240.786446 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X281.988572 Y136.08234 Z4 E11248.807714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X282.813472 Y137.826444 Z4 E11256.828982 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.463447 Y139.643003 Z4 E11264.850249 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.932239 Y141.514524 Z4 E11272.871517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.215332 Y143.422983 Z4 E11280.892784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.31 Y145.35 Z4 E11288.914052 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.215332 Y147.277017 Z4 E11296.93532 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.932239 Y149.185476 Z4 E11304.956587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.463447 Y151.056997 Z4 E11312.977855 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X282.813472 Y152.873556 Z4 E11320.999122 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X281.988572 Y154.61766 Z4 E11329.02039 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X280.996693 Y156.272511 Z4 E11337.041657 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X279.847386 Y157.822172 Z4 E11345.062925 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X278.551719 Y159.251719 Z4 E11353.084193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.122172 Y160.547386 Z4 E11361.10546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.572511 Y161.696693 Z4 E11369.126728 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X273.91766 Y162.688572 Z4 E11377.147995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.173556 Y163.513472 Z4 E11385.169263 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X270.356997 Y164.163447 Z4 E11393.190531 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X268.485476 Y164.632239 Z4 E11401.211798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X266.577017 Y164.915332 Z4 E11409.233066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X264.65 Y165.01 Z4 E11417.254333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X262.722983 Y164.915332 Z4 E11425.275601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.814524 Y164.632239 Z4 E11433.296869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.943003 Y164.163447 Z4 E11441.318136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X257.126444 Y163.513472 Z4 E11449.339404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.38234 Y162.688572 Z4 E11457.360671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.727489 Y161.696693 Z4 E11465.381939 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.177828 Y160.547386 Z4 E11473.403206 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.748281 Y159.251719 Z4 E11481.424474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.452614 Y157.822172 Z4 E11489.445742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.303307 Y156.272511 Z4 E11497.467009 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.311428 Y154.61766 Z4 E11505.488277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.486528 Y152.873556 Z4 E11513.509544 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.836553 Y151.056997 Z4 E11521.530812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.367761 Y149.185476 Z4 E11529.55208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.084668 Y147.277017 Z4 E11537.573347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.99 Y145.35 Z4 E11545.594615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.084668 Y143.422983 Z4 E11553.615882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.367761 Y141.514524 Z4 E11561.63715 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.6 Y140.587376 Z4 E11565.610873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.832239 Y141.514524 Z4 E11569.584596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.115332 Y143.422983 Z4 E11577.605864 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.21 Y145.35 Z4 E11585.627131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.115332 Y147.277017 Z4 E11593.648399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.832239 Y149.185476 Z4 E11601.669666 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.363447 Y151.056997 Z4 E11609.690934 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.713472 Y152.873556 Z4 E11617.712202 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.888572 Y154.61766 Z4 E11625.733469 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.896693 Y156.272511 Z4 E11633.754737 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.747386 Y157.822172 Z4 E11641.776004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X240.451719 Y159.251719 Z4 E11649.797272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X239.022172 Y160.547386 Z4 E11657.81854 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.472511 Y161.696693 Z4 E11665.839807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X235.81766 Y162.688572 Z4 E11673.861075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.851452 Y163.145554 Z4 E11678.304741 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.971884 Y163.016193 Z4 E11679.039555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X236.446584 Y161.579041 Z4 E11687.600554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.848614 Y160.358888 Z4 E11695.327788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X239.180484 Y159.345078 Z4 E11702.286745 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X240.444709 Y158.526953 Z4 E11708.547352 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.643799 Y157.893857 Z4 E11714.184778 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.780267 Y157.435134 Z4 E11719.280048 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.856625 Y157.140125 Z4 E11723.920062 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.875385 Y156.998175 Z4 E11728.196493 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.839061 Y156.998627 Z4 E11732.202989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.750162 Y157.130824 Z4 E11736.030575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.611203 Y157.384109 Z4 E11739.762036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.424695 Y157.747826 Z4 E11743.466799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.19315 Y158.211318 Z4 E11747.197805 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.605 Y159.395 Z4 E11754.857596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X251.788682 Y160.80685 Z4 E11762.517387 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.252174 Y161.575305 Z4 E11766.248392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.615891 Y162.388797 Z4 E11769.953156 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.869176 Y163.249838 Z4 E11773.684616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.001373 Y164.160939 Z4 E11777.512203 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.001825 Y165.124615 Z4 E11781.518698 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.859875 Y166.143375 Z4 E11785.79513 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.564866 Y167.219733 Z4 E11790.435144 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.106143 Y168.356201 Z4 E11795.530413 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X251.473047 Y169.555291 Z4 E11801.16784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.654922 Y170.819516 Z4 E11807.428446 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.641112 Y172.151386 Z4 E11814.387403 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.420959 Y173.553416 Z4 E11822.114637 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.983807 Y175.028116 Z4 E11830.675636 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.319 Y176.578 Z4 E11840.132248 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.951602 Y178.261771 Z4 E11849.150194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.7375 Y180.555797 Z4 E11862.405306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X238.721086 Y183.276268 Z4 E11879.293073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.94675 Y186.239375 Z4 E11899.242925 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X232.789233 Y187.754477 Z4 E11910.203651 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X230.458883 Y189.261311 Z4 E11921.741101 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X227.961247 Y190.736899 Z4 E11933.801874 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X225.301875 Y192.158266 Z4 E11946.338386 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.486315 Y193.502435 Z4 E11959.309684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.520117 Y194.746432 Z4 E11972.682328 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X216.408829 Y195.867279 Z4 E11986.431339 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.158 Y196.842 Z4 E12000.541177 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.888154 Y197.111846 Z4 E12002.12777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.835798 Y198.266555 Z4 E12008.33819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.539962 Y199.583952 Z4 E12014.548611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.973584 Y201.013412 Z4 E12020.759031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.12 Y202.5 Z4 E12026.969452 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.501 Y202.5 Z4 E12028.553466 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X217.285212 Y201.225894 Z4 E12037.668539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.072193 Y200.111695 Z4 E12046.423782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X220.849903 Y199.147649 Z4 E12054.831464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.606297 Y198.324 Z4 E12062.896746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.329334 Y197.630991 Z4 E12070.618002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X226.006971 Y197.058867 Z4 E12077.987243 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X229.177875 Y196.23825 Z4 E12091.604647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X232.02267 Y195.784102 Z4 E12103.581694 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.445016 Y195.618375 Z4 E12113.67618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X236.348572 Y195.663023 Z4 E12121.592425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.637 Y195.84 Z4 E12126.999382 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X238.994337 Y195.775642 Z4 E12132.648873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.330964 Y195.898469 Z4 E12142.376851 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.321375 Y196.076531 Z4 E12146.560521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.974195 Y196.643145 Z4 E12153.824722 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.647726 Y197.022573 Z4 E12157.038697 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.22675 Y197.46 Z4 E12160.055725 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.716829 Y197.950865 Z4 E12162.939513 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.452394 Y199.074661 Z4 E12168.523558 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.709 Y199.698469 Z4 E12171.327906 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.027664 Y201.047098 Z4 E12177.08925 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.124 Y202.5 Z4 E12183.14298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.027664 Y203.952902 Z4 E12189.19671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.709 Y205.301531 Z4 E12194.958054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.452394 Y205.925339 Z4 E12197.762402 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.716829 Y207.049135 Z4 E12203.346447 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.22675 Y207.54 Z4 E12206.230235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.647726 Y207.977427 Z4 E12209.247263 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.974195 Y208.356855 Z4 E12212.461238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.321375 Y208.923469 Z4 E12219.725439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.330964 Y209.101531 Z4 E12223.909109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X238.994337 Y209.224358 Z4 E12233.637087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.637 Y209.16 Z4 E12239.286578 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X236.348572 Y209.336977 Z4 E12244.693535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.445016 Y209.381625 Z4 E12252.60978 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X232.02267 Y209.215898 Z4 E12262.704266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X229.177875 Y208.76175 Z4 E12274.681313 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X226.006971 Y207.941133 Z4 E12288.298717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.329334 Y207.369009 Z4 E12295.667958 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.606297 Y206.676 Z4 E12303.389214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X220.849903 Y205.852351 Z4 E12311.454496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.072193 Y204.888305 Z4 E12319.862178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X217.285212 Y203.774106 Z4 E12328.61742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.501 Y202.5 Z4 E12337.732494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.12 Y202.5 Z4 E12339.316508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.973584 Y203.986588 Z4 E12345.526928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.539962 Y205.416048 Z4 E12351.737349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.835798 Y206.733445 Z4 E12357.94777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.888154 Y207.888154 Z4 E12364.15819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X211.733445 Y208.835798 Z4 E12370.368611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.416048 Y209.539962 Z4 E12376.579032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.986588 Y209.973584 Z4 E12382.789452 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y210.12 Z4 E12388.999873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y210.501 Z4 E12390.583887 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.774106 Y212.285212 Z4 E12399.69896 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X209.888305 Y214.072193 Z4 E12408.454203 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.852351 Y215.849903 Z4 E12416.861884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X211.676 Y217.606297 Z4 E12424.927166 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.369009 Y219.329334 Z4 E12432.648423 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.941133 Y221.006971 Z4 E12440.017663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.76175 Y224.177875 Z4 E12453.635068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.215898 Y227.02267 Z4 E12465.612115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.381625 Y229.445016 Z4 E12475.7066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.336977 Y231.348572 Z4 E12483.622846 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.16 Y232.637 Z4 E12489.029803 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.224358 Y233.994337 Z4 E12494.679294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.101531 Y236.330964 Z4 E12504.407272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.923469 Y237.321375 Z4 E12508.590941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.356855 Y238.974195 Z4 E12515.855143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.977427 Y239.647726 Z4 E12519.069118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.54 Y240.22675 Z4 E12522.086146 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.049135 Y240.716829 Z4 E12524.969934 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.925339 Y241.452394 Z4 E12530.553979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.301531 Y241.709 Z4 E12533.358327 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.952902 Y242.027664 Z4 E12539.119671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y242.124 Z4 E12545.173401 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.047098 Y242.027664 Z4 E12551.227131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.698469 Y241.709 Z4 E12556.988475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.074661 Y241.452394 Z4 E12559.792822 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.950865 Y240.716829 Z4 E12565.376868 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.46 Y240.22675 Z4 E12568.260656 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.022573 Y239.647726 Z4 E12571.277684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.643145 Y238.974195 Z4 E12574.491659 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.076531 Y237.321375 Z4 E12581.75586 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.898469 Y236.330964 Z4 E12585.939529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.775642 Y233.994337 Z4 E12595.667508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.84 Y232.637 Z4 E12601.316999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.663023 Y231.348572 Z4 E12606.723956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.618375 Y229.445016 Z4 E12614.640201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.784102 Y227.02267 Z4 E12624.734686 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.23825 Y224.177875 Z4 E12636.711733 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.058867 Y221.006971 Z4 E12650.329138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.630991 Y219.329334 Z4 E12657.698378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X203.324 Y217.606297 Z4 E12665.419635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.147649 Y215.849903 Z4 E12673.484917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X205.111695 Y214.072193 Z4 E12681.892599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.225894 Y212.285212 Z4 E12690.647841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y210.501 Z4 E12699.762915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y210.12 Z4 E12701.346929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.013412 Y209.973584 Z4 E12707.557349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.583952 Y209.539962 Z4 E12713.76777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X203.266555 Y208.835798 Z4 E12719.978191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.111846 Y207.888154 Z4 E12726.188611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.164202 Y206.733445 Z4 E12732.399032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.460038 Y205.416048 Z4 E12738.609453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.026416 Y203.986588 Z4 E12744.819873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.88 Y202.5 Z4 E12751.030294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.499 Y202.5 Z4 E12752.614308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X197.714788 Y203.774106 Z4 E12761.729381 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.927807 Y204.888305 Z4 E12770.484623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X194.150097 Y205.852351 Z4 E12778.892305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.393703 Y206.676 Z4 E12786.957587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X190.670666 Y207.369009 Z4 E12794.678844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X188.993029 Y207.941133 Z4 E12802.048084 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X185.822125 Y208.76175 Z4 E12815.665489 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X182.97733 Y209.215898 Z4 E12827.642536 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.554984 Y209.381625 Z4 E12837.737021 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X178.651428 Y209.336977 Z4 E12845.653267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X177.363 Y209.16 Z4 E12851.060224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X176.005663 Y209.224358 Z4 E12856.709715 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.669036 Y209.101531 Z4 E12866.437693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X172.678625 Y208.923469 Z4 E12870.621362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.025805 Y208.356855 Z4 E12877.885563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.352274 Y207.977427 Z4 E12881.099539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.77325 Y207.54 Z4 E12884.116567 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.283171 Y207.049135 Z4 E12887.000355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.547606 Y205.925339 Z4 E12892.5844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.291 Y205.301531 Z4 E12895.388747 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.972336 Y203.952902 Z4 E12901.150092 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.876 Y202.5 Z4 E12907.203822 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.972336 Y201.047098 Z4 E12913.257552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.291 Y199.698469 Z4 E12919.018896 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.547606 Y199.074661 Z4 E12921.823243 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.283171 Y197.950865 Z4 E12927.407289 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.77325 Y197.46 Z4 E12930.291077 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.352274 Y197.022573 Z4 E12933.308105 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.025805 Y196.643145 Z4 E12936.52208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X172.678625 Y196.076531 Z4 E12943.786281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.669036 Y195.898469 Z4 E12947.96995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X176.005663 Y195.775642 Z4 E12957.697929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X177.363 Y195.84 Z4 E12963.34742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X178.651428 Y195.663023 Z4 E12968.754377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.554984 Y195.618375 Z4 E12976.670622 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X182.97733 Y195.784102 Z4 E12986.765107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X185.822125 Y196.23825 Z4 E12998.742154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X188.993029 Y197.058867 Z4 E13012.359559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X190.670666 Y197.630991 Z4 E13019.728799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.393703 Y198.324 Z4 E13027.450056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X194.150097 Y199.147649 Z4 E13035.515338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.927807 Y200.111695 Z4 E13043.92302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X197.714788 Y201.225894 Z4 E13052.678262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.499 Y202.5 Z4 E13061.793336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.88 Y202.5 Z4 E13063.37735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.026416 Y201.013412 Z4 E13069.58777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.460038 Y199.583952 Z4 E13075.798191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.164202 Y198.266555 Z4 E13082.008612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.111846 Y197.111846 Z4 E13088.219032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X203.266555 Y196.164202 Z4 E13094.429453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.583952 Y195.460038 Z4 E13100.639873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.013412 Y195.026416 Z4 E13106.850294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y194.88 Z4 E13113.060715 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y194.499 Z4 E13114.644729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.225894 Y192.714788 Z4 E13123.759802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X205.111695 Y190.927807 Z4 E13132.515044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.147649 Y189.150097 Z4 E13140.922726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X203.324 Y187.393703 Z4 E13148.988008 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.630991 Y185.670666 Z4 E13156.709265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.058867 Y183.993029 Z4 E13164.078505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.23825 Y180.822125 Z4 E13177.69591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.784102 Y177.97733 Z4 E13189.672957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.618375 Y175.554984 Z4 E13199.767442 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.663023 Y173.651428 Z4 E13207.683688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.84 Y172.363 Z4 E13213.090645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.775642 Y171.005663 Z4 E13218.740136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.898469 Y168.669036 Z4 E13228.468114 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.076531 Y167.678625 Z4 E13232.651783 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.643145 Y166.025805 Z4 E13239.915984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.022573 Y165.352274 Z4 E13243.12996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.46 Y164.77325 Z4 E13246.146988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.950865 Y164.283171 Z4 E13249.030775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.074661 Y163.547606 Z4 E13254.614821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.698469 Y163.291 Z4 E13257.419168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.047098 Y162.972336 Z4 E13263.180513 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y162.876 Z4 E13269.234243 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.952902 Y162.972336 Z4 E13275.287972 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.301531 Y163.291 Z4 E13281.049317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.925339 Y163.547606 Z4 E13283.853664 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.049135 Y164.283171 Z4 E13289.43771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.54 Y164.77325 Z4 E13292.321498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.977427 Y165.352274 Z4 E13295.338526 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.356855 Y166.025805 Z4 E13298.552501 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.923469 Y167.678625 Z4 E13305.816702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.101531 Y168.669036 Z4 E13310.000371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.224358 Y171.005663 Z4 E13319.72835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.16 Y172.363 Z4 E13325.37784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.336977 Y173.651428 Z4 E13330.784797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.381625 Y175.554984 Z4 E13338.701043 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.215898 Y177.97733 Z4 E13348.795528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.76175 Y180.822125 Z4 E13360.772575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.941133 Y183.993029 Z4 E13374.38998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.369009 Y185.670666 Z4 E13381.75922 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X211.676 Y187.393703 Z4 E13389.480477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.852351 Y189.150097 Z4 E13397.545759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X209.888305 Y190.927807 Z4 E13405.953441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.774106 Y192.714788 Z4 E13414.708683 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y194.499 Z4 E13423.823757 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y194.88 Z4 E13425.407771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.986588 Y195.026416 Z4 E13431.618191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.416048 Y195.460038 Z4 E13437.828612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X211.733445 Y196.164202 Z4 E13444.039032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.888154 Y197.111846 Z4 E13450.249453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.158 Y196.842 Z4 E13451.836046 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.132721 Y193.591171 Z4 E13465.945884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.253568 Y190.479883 Z4 E13479.694894 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X216.497565 Y187.513685 Z4 E13493.067539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X217.841734 Y184.698125 Z4 E13506.038837 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.263101 Y182.038753 Z4 E13518.575349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X220.738689 Y179.541117 Z4 E13530.636122 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.245523 Y177.210767 Z4 E13542.173572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X223.760625 Y175.05325 Z4 E13553.134298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X226.723732 Y171.278914 Z4 E13573.084149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X229.444203 Y168.2625 Z4 E13589.971917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X231.738229 Y166.048398 Z4 E13603.227029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X233.422 Y164.681 Z4 E13612.244974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.851452 Y163.145554 Z4 E13620.966772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.073556 Y163.513472 Z4 E13624.544373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X232.256997 Y164.163447 Z4 E13632.565641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X230.385476 Y164.632239 Z4 E13640.586909 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X228.477017 Y164.915332 Z4 E13648.608176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X226.55 Y165.01 Z4 E13656.629444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.622983 Y164.915332 Z4 E13664.650711 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.714524 Y164.632239 Z4 E13672.671979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X220.843003 Y164.163447 Z4 E13680.693246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.026444 Y163.513472 Z4 E13688.714514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X217.28234 Y162.688572 Z4 E13696.735782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.627489 Y161.696693 Z4 E13704.757049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.077828 Y160.547386 Z4 E13712.778317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.648281 Y159.251719 Z4 E13720.799584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X211.352614 Y157.822172 Z4 E13728.820852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.203307 Y156.272511 Z4 E13736.84212 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X209.211428 Y154.61766 Z4 E13744.863387 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.386528 Y152.873556 Z4 E13752.884655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.736553 Y151.056997 Z4 E13760.905922 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.267761 Y149.185476 Z4 E13768.92719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.984668 Y147.277017 Z4 E13776.948458 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.89 Y145.35 Z4 E13784.969725 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.984668 Y143.422983 Z4 E13792.990993 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.267761 Y141.514524 Z4 E13801.01226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y140.587376 Z4 E13804.985983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.732239 Y141.514524 Z4 E13808.959706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.015332 Y143.422983 Z4 E13816.980974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.11 Y145.35 Z4 E13825.002242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.015332 Y147.277017 Z4 E13833.023509 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.732239 Y149.185476 Z4 E13841.044777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.263447 Y151.056997 Z4 E13849.066044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.613472 Y152.873556 Z4 E13857.087312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X205.788572 Y154.61766 Z4 E13865.10858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.796693 Y156.272511 Z4 E13873.129847 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X203.647386 Y157.822172 Z4 E13881.151115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.351719 Y159.251719 Z4 E13889.172382 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.922172 Y160.547386 Z4 E13897.19365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.372511 Y161.696693 Z4 E13905.214918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X197.71766 Y162.688572 Z4 E13913.236185 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.973556 Y163.513472 Z4 E13921.257453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X194.156997 Y164.163447 Z4 E13929.27872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.285476 Y164.632239 Z4 E13937.299988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X190.377017 Y164.915332 Z4 E13945.321255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X188.45 Y165.01 Z4 E13953.342523 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X186.522983 Y164.915332 Z4 E13961.363791 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X184.614524 Y164.632239 Z4 E13969.385058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X182.743003 Y164.163447 Z4 E13977.406326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.926444 Y163.513472 Z4 E13985.427593 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X179.18234 Y162.688572 Z4 E13993.448861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X177.527489 Y161.696693 Z4 E14001.470129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X175.977828 Y160.547386 Z4 E14009.491396 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X174.548281 Y159.251719 Z4 E14017.512664 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.252614 Y157.822172 Z4 E14025.533931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X172.103307 Y156.272511 Z4 E14033.555199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.111428 Y154.61766 Z4 E14041.576467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.286528 Y152.873556 Z4 E14049.597734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.636553 Y151.056997 Z4 E14057.619002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.167761 Y149.185476 Z4 E14065.640269 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.884668 Y147.277017 Z4 E14073.661537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.79 Y145.35 Z4 E14081.682804 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.884668 Y143.422983 Z4 E14089.704072 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.167761 Y141.514524 Z4 E14097.72534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.4 Y140.587376 Z4 E14101.699063 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.632239 Y141.514524 Z4 E14105.672786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.915332 Y143.422983 Z4 E14113.694053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.01 Y145.35 Z4 E14121.715321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.915332 Y147.277017 Z4 E14129.736589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.632239 Y149.185476 Z4 E14137.757856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.163447 Y151.056997 Z4 E14145.779124 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.513472 Y152.873556 Z4 E14153.800391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.688572 Y154.61766 Z4 E14161.821659 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.696693 Y156.272511 Z4 E14169.842927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.547386 Y157.822172 Z4 E14177.864194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.251719 Y159.251719 Z4 E14185.885462 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.822172 Y160.547386 Z4 E14193.906729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.272511 Y161.696693 Z4 E14201.927997 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X159.61766 Y162.688572 Z4 E14209.949264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X157.873556 Y163.513472 Z4 E14217.970532 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X156.056997 Y164.163447 Z4 E14225.9918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X155.112624 Y164.4 Z4 E14230.039344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X156.056997 Y164.636553 Z4 E14234.086889 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X157.873556 Y165.286528 Z4 E14242.108156 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X159.61766 Y166.111428 Z4 E14250.129424 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.272511 Y167.103307 Z4 E14258.150691 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.822172 Y168.252614 Z4 E14266.171959 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.251719 Y169.548281 Z4 E14274.193227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.547386 Y170.977828 Z4 E14282.214494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.696693 Y172.527489 Z4 E14290.235762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.688572 Y174.18234 Z4 E14298.257029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.145554 Y175.148548 Z4 E14302.700695 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.016193 Y175.028116 Z4 E14303.43551 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.579041 Y173.553416 Z4 E14311.996509 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.358888 Y172.151386 Z4 E14319.723743 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.345078 Y170.819516 Z4 E14326.6827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X163.526953 Y169.555291 Z4 E14332.943306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.893857 Y168.356201 Z4 E14338.580733 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.435134 Y167.219733 Z4 E14343.676002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.140125 Y166.143375 Z4 E14348.316016 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.998175 Y165.124615 Z4 E14352.592448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.998627 Y164.160939 Z4 E14356.598943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.130824 Y163.249838 Z4 E14360.42653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.384109 Y162.388797 Z4 E14364.15799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.747826 Y161.575305 Z4 E14367.862754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X163.211318 Y160.80685 Z4 E14371.59376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.395 Y159.395 Z4 E14379.25355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.80685 Y158.211318 Z4 E14386.913341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.575305 Y157.747826 Z4 E14390.644347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.388797 Y157.384109 Z4 E14394.34911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.249838 Y157.130824 Z4 E14398.080571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.160939 Y156.998627 Z4 E14401.908157 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.124615 Y156.998175 Z4 E14405.914653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.143375 Y157.140125 Z4 E14410.191084 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X172.219733 Y157.435134 Z4 E14414.831099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.356201 Y157.893857 Z4 E14419.926368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X174.555291 Y158.526953 Z4 E14425.563794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X175.819516 Y159.345078 Z4 E14431.824401 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X177.151386 Y160.358888 Z4 E14438.783358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X178.553416 Y161.579041 Z4 E14446.510592 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.028116 Y163.016193 Z4 E14455.071591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X181.578 Y164.681 Z4 E14464.528203 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X183.261771 Y166.048398 Z4 E14473.546148 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X185.555797 Y168.2625 Z4 E14486.80126 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X188.276268 Y171.278914 Z4 E14503.689028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.239375 Y175.05325 Z4 E14523.638879 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.754477 Y177.210767 Z4 E14534.599605 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X194.261311 Y179.541117 Z4 E14546.137056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.736899 Y182.038753 Z4 E14558.197828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X197.158266 Y184.698125 Z4 E14570.73434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X198.502435 Y187.513685 Z4 E14583.705638 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.746432 Y190.479883 Z4 E14597.078283 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.867279 Y193.591171 Z4 E14610.827293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.842 Y196.842 Z4 E14624.937131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X198.591171 Y195.867279 Z4 E14639.046969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.479883 Y194.746432 Z4 E14652.795979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.513685 Y193.502435 Z4 E14666.168624 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X189.698125 Y192.158266 Z4 E14679.139922 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X187.038753 Y190.736899 Z4 E14691.676434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X184.541117 Y189.261311 Z4 E14703.737207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X182.210767 Y187.754477 Z4 E14715.274657 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.05325 Y186.239375 Z4 E14726.235383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X176.278914 Y183.276268 Z4 E14746.185234 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.2625 Y180.555797 Z4 E14763.073002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.048398 Y178.261771 Z4 E14776.328114 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.681 Y176.578 Z4 E14785.346059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.145554 Y175.148548 Z4 E14794.067857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.513472 Y175.926444 Z4 E14797.645458 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.163447 Y177.743003 Z4 E14805.666726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.632239 Y179.614524 Z4 E14813.687994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.915332 Y181.522983 Z4 E14821.709261 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.01 Y183.45 Z4 E14829.730529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.915332 Y185.377017 Z4 E14837.751796 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.632239 Y187.285476 Z4 E14845.773064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.163447 Y189.156997 Z4 E14853.794332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.513472 Y190.973556 Z4 E14861.815599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.688572 Y192.71766 Z4 E14869.836867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.696693 Y194.372511 Z4 E14877.858134 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.547386 Y195.922172 Z4 E14885.879402 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.251719 Y197.351719 Z4 E14893.900669 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.822172 Y198.647386 Z4 E14901.921937 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.272511 Y199.796693 Z4 E14909.943205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X159.61766 Y200.788572 Z4 E14917.964472 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X157.873556 Y201.613472 Z4 E14925.98574 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X156.056997 Y202.263447 Z4 E14934.007007 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X155.112624 Y202.5 Z4 E14938.054552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X156.056997 Y202.736553 Z4 E14942.102096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X157.873556 Y203.386528 Z4 E14950.123364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X159.61766 Y204.211428 Z4 E14958.144632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.272511 Y205.203307 Z4 E14966.165899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.822172 Y206.352614 Z4 E14974.187167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.251719 Y207.648281 Z4 E14982.208434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.547386 Y209.077828 Z4 E14990.229702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.696693 Y210.627489 Z4 E14998.250969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.688572 Y212.28234 Z4 E15006.272237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.513472 Y214.026444 Z4 E15014.293505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.163447 Y215.843003 Z4 E15022.314772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.632239 Y217.714524 Z4 E15030.33604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.915332 Y219.622983 Z4 E15038.357307 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.01 Y221.55 Z4 E15046.378575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.915332 Y223.477017 Z4 E15054.399843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.632239 Y225.385476 Z4 E15062.42111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.163447 Y227.256997 Z4 E15070.442378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.513472 Y229.073556 Z4 E15078.463645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.688572 Y230.81766 Z4 E15086.484913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.696693 Y232.472511 Z4 E15094.506181 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.547386 Y234.022172 Z4 E15102.527448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.251719 Y235.451719 Z4 E15110.548716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.869279 Y236.70469 Z4 E15118.305661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.893857 Y236.643799 Z4 E15118.578661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X163.526953 Y235.444709 Z4 E15124.216088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.345078 Y234.180484 Z4 E15130.476695 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.358888 Y232.848614 Z4 E15137.435652 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.579041 Y231.446584 Z4 E15145.162886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.016193 Y229.971884 Z4 E15153.723884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.681 Y228.422 Z4 E15163.180497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.048398 Y226.738229 Z4 E15172.198442 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.2625 Y224.444203 Z4 E15185.453554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X176.278914 Y221.723732 Z4 E15202.341321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.05325 Y218.760625 Z4 E15222.291173 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X182.210767 Y217.245523 Z4 E15233.251899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X184.541117 Y215.738689 Z4 E15244.789349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X187.038753 Y214.263101 Z4 E15256.850122 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X189.698125 Y212.841734 Z4 E15269.386634 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.513685 Y211.497565 Z4 E15282.357932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.479883 Y210.253568 Z4 E15295.730576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X198.591171 Y209.132721 Z4 E15309.479587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X201.842 Y208.158 Z4 E15323.589425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.867279 Y211.408829 Z4 E15337.699263 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.746432 Y214.520117 Z4 E15351.448273 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X198.502435 Y217.486315 Z4 E15364.820918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X197.158266 Y220.301875 Z4 E15377.792215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.736899 Y222.961247 Z4 E15390.328728 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X194.261311 Y225.458883 Z4 E15402.3895 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.754477 Y227.789233 Z4 E15413.926951 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.239375 Y229.94675 Z4 E15424.887677 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X188.276268 Y233.721086 Z4 E15444.837528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X185.555797 Y236.7375 Z4 E15461.725295 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X183.261771 Y238.951602 Z4 E15474.980407 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X181.578 Y240.319 Z4 E15483.998353 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.028116 Y241.983807 Z4 E15493.454965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X178.553416 Y243.420959 Z4 E15502.015964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X177.151386 Y244.641112 Z4 E15509.743198 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X175.819516 Y245.654922 Z4 E15516.702155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X174.555291 Y246.473047 Z4 E15522.962762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.356201 Y247.106143 Z4 E15528.600188 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X172.219733 Y247.564866 Z4 E15533.695457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.143375 Y247.859875 Z4 E15538.335471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.124615 Y248.001825 Z4 E15542.611903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.160939 Y248.001373 Z4 E15546.618399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.249838 Y247.869176 Z4 E15550.445985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.388797 Y247.615891 Z4 E15554.177446 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.575305 Y247.252174 Z4 E15557.882209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.80685 Y246.788682 Z4 E15561.613215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.395 Y245.605 Z4 E15569.273006 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X163.211318 Y244.19315 Z4 E15576.932796 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.747826 Y243.424695 Z4 E15580.663802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.384109 Y242.611203 Z4 E15584.368565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.130824 Y241.750162 Z4 E15588.100026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.998627 Y240.839061 Z4 E15591.927612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.998175 Y239.875385 Z4 E15595.934108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.140125 Y238.856625 Z4 E15600.21054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.435134 Y237.780267 Z4 E15604.850554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.869279 Y236.70469 Z4 E15609.672823 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.822172 Y236.747386 Z4 E15609.937145 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.272511 Y237.896693 Z4 E15617.958412 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X159.61766 Y238.888572 Z4 E15625.97968 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X157.873556 Y239.713472 Z4 E15634.000948 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X156.056997 Y240.363447 Z4 E15642.022215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X155.112624 Y240.6 Z4 E15646.06976 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X156.056997 Y240.836553 Z4 E15650.117304 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X157.873556 Y241.486528 Z4 E15658.138572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X159.61766 Y242.311428 Z4 E15666.159839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.272511 Y243.303307 Z4 E15674.181107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.822172 Y244.452614 Z4 E15682.202374 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.251719 Y245.748281 Z4 E15690.223642 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.547386 Y247.177828 Z4 E15698.24491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.696693 Y248.727489 Z4 E15706.266177 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.688572 Y250.38234 Z4 E15714.287445 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.513472 Y252.126444 Z4 E15722.308712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.163447 Y253.943003 Z4 E15730.32998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.4 Y254.887376 Z4 E15734.377524 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.636553 Y253.943003 Z4 E15738.425069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.286528 Y252.126444 Z4 E15746.446337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.111428 Y250.38234 Z4 E15754.467604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X172.103307 Y248.727489 Z4 E15762.488872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.252614 Y247.177828 Z4 E15770.510139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X174.548281 Y245.748281 Z4 E15778.531407 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X175.977828 Y244.452614 Z4 E15786.552674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X177.527489 Y243.303307 Z4 E15794.573942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X179.18234 Y242.311428 Z4 E15802.59521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.926444 Y241.486528 Z4 E15810.616477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X182.743003 Y240.836553 Z4 E15818.637745 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X184.614524 Y240.367761 Z4 E15826.659012 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X186.522983 Y240.084668 Z4 E15834.68028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X188.45 Y239.99 Z4 E15842.701548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X190.377017 Y240.084668 Z4 E15850.722815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.285476 Y240.367761 Z4 E15858.744083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X194.156997 Y240.836553 Z4 E15866.76535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.973556 Y241.486528 Z4 E15874.786618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X197.71766 Y242.311428 Z4 E15882.807886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.372511 Y243.303307 Z4 E15890.829153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.922172 Y244.452614 Z4 E15898.850421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.351719 Y245.748281 Z4 E15906.871688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X203.647386 Y247.177828 Z4 E15914.892956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.796693 Y248.727489 Z4 E15922.914223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X205.788572 Y250.38234 Z4 E15930.935491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.613472 Y252.126444 Z4 E15938.956759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.263447 Y253.943003 Z4 E15946.978026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y254.887376 Z4 E15951.025571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.736553 Y253.943003 Z4 E15955.073115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.386528 Y252.126444 Z4 E15963.094383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X209.211428 Y250.38234 Z4 E15971.11565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.203307 Y248.727489 Z4 E15979.136918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X211.352614 Y247.177828 Z4 E15987.158186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.648281 Y245.748281 Z4 E15995.179453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.077828 Y244.452614 Z4 E16003.200721 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.627489 Y243.303307 Z4 E16011.221988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X217.28234 Y242.311428 Z4 E16019.243256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.026444 Y241.486528 Z4 E16027.264523 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X220.843003 Y240.836553 Z4 E16035.285791 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.714524 Y240.367761 Z4 E16043.307059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.622983 Y240.084668 Z4 E16051.328326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X226.55 Y239.99 Z4 E16059.349594 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X228.477017 Y240.084668 Z4 E16067.370861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X230.385476 Y240.367761 Z4 E16075.392129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X232.256997 Y240.836553 Z4 E16083.413397 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.073556 Y241.486528 Z4 E16091.434664 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X235.81766 Y242.311428 Z4 E16099.455932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.472511 Y243.303307 Z4 E16107.477199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X239.022172 Y244.452614 Z4 E16115.498467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X240.451719 Y245.748281 Z4 E16123.519735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.70469 Y247.130721 Z4 E16131.27668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.643799 Y247.106143 Z4 E16131.54968 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X240.444709 Y246.473047 Z4 E16137.187107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X239.180484 Y245.654922 Z4 E16143.447713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.848614 Y244.641112 Z4 E16150.406671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X236.446584 Y243.420959 Z4 E16158.133904 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.971884 Y241.983807 Z4 E16166.694903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X233.422 Y240.319 Z4 E16176.151516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X231.738229 Y238.951602 Z4 E16185.169461 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X229.444203 Y236.7375 Z4 E16198.424573 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X226.723732 Y233.721086 Z4 E16215.31234 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X223.760625 Y229.94675 Z4 E16235.262192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.245523 Y227.789233 Z4 E16246.222918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X220.738689 Y225.458883 Z4 E16257.760368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.263101 Y222.961247 Z4 E16269.821141 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X217.841734 Y220.301875 Z4 E16282.357653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X216.497565 Y217.486315 Z4 E16295.328951 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.253568 Y214.520117 Z4 E16308.701595 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.132721 Y211.408829 Z4 E16322.450606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X213.158 Y208.158 Z4 E16336.560444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X216.408829 Y209.132721 Z4 E16350.670282 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.520117 Y210.253568 Z4 E16364.419292 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.486315 Y211.497565 Z4 E16377.791936 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X225.301875 Y212.841734 Z4 E16390.763234 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X227.961247 Y214.263101 Z4 E16403.299746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X230.458883 Y215.738689 Z4 E16415.360519 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X232.789233 Y217.245523 Z4 E16426.89797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.94675 Y218.760625 Z4 E16437.858696 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X238.721086 Y221.723732 Z4 E16457.808547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.7375 Y224.444203 Z4 E16474.696314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.951602 Y226.738229 Z4 E16487.951426 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.319 Y228.422 Z4 E16496.969372 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.983807 Y229.971884 Z4 E16506.425984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.420959 Y231.446584 Z4 E16514.986983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.641112 Y232.848614 Z4 E16522.714217 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.654922 Y234.180484 Z4 E16529.673174 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X251.473047 Y235.444709 Z4 E16535.93378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.106143 Y236.643799 Z4 E16541.571207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.564866 Y237.780267 Z4 E16546.666476 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.859875 Y238.856625 Z4 E16551.30649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.001825 Y239.875385 Z4 E16555.582922 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.001373 Y240.839061 Z4 E16559.589417 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.869176 Y241.750162 Z4 E16563.417004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.615891 Y242.611203 Z4 E16567.148465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.252174 Y243.424695 Z4 E16570.853228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X251.788682 Y244.19315 Z4 E16574.584234 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.605 Y245.605 Z4 E16582.244024 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.19315 Y246.788682 Z4 E16589.903815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.424695 Y247.252174 Z4 E16593.634821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.611203 Y247.615891 Z4 E16597.339584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.750162 Y247.869176 Z4 E16601.071045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.839061 Y248.001373 Z4 E16604.898631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.875385 Y248.001825 Z4 E16608.905127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.856625 Y247.859875 Z4 E16613.181559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.780267 Y247.564866 Z4 E16617.821573 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.70469 Y247.130721 Z4 E16622.643841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.747386 Y247.177828 Z4 E16622.908164 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.896693 Y248.727489 Z4 E16630.929431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.888572 Y250.38234 Z4 E16638.950699 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.713472 Y252.126444 Z4 E16646.971966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.363447 Y253.943003 Z4 E16654.993234 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.6 Y254.887376 Z4 E16659.040778 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.836553 Y253.943003 Z4 E16663.088323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.486528 Y252.126444 Z4 E16671.109591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.311428 Y250.38234 Z4 E16679.130858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.303307 Y248.727489 Z4 E16687.152126 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.452614 Y247.177828 Z4 E16695.173393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.748281 Y245.748281 Z4 E16703.194661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.177828 Y244.452614 Z4 E16711.215928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.727489 Y243.303307 Z4 E16719.237196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.38234 Y242.311428 Z4 E16727.258464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X257.126444 Y241.486528 Z4 E16735.279731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.943003 Y240.836553 Z4 E16743.300999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.814524 Y240.367761 Z4 E16751.322266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X262.722983 Y240.084668 Z4 E16759.343534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X264.65 Y239.99 Z4 E16767.364802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X266.577017 Y240.084668 Z4 E16775.386069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X268.485476 Y240.367761 Z4 E16783.407337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X269.412624 Y240.6 Z4 E16787.38106 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X268.485476 Y240.832239 Z4 E16791.354783 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X266.577017 Y241.115332 Z4 E16799.376051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X264.65 Y241.21 Z4 E16807.397318 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X262.722983 Y241.115332 Z4 E16815.418586 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.814524 Y240.832239 Z4 E16823.439853 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.943003 Y240.363447 Z4 E16831.461121 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X257.126444 Y239.713472 Z4 E16839.482388 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.38234 Y238.888572 Z4 E16847.503656 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.727489 Y237.896693 Z4 E16855.524924 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.177828 Y236.747386 Z4 E16863.546191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.748281 Y235.451719 Z4 E16871.567459 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.452614 Y234.022172 Z4 E16879.588726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.303307 Y232.472511 Z4 E16887.609994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.311428 Y230.81766 Z4 E16895.631262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.486528 Y229.073556 Z4 E16903.652529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.836553 Y227.256997 Z4 E16911.673797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.367761 Y225.385476 Z4 E16919.695064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.084668 Y223.477017 Z4 E16927.716332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.99 Y221.55 Z4 E16935.7376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.084668 Y219.622983 Z4 E16943.758867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.367761 Y217.714524 Z4 E16951.780135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.836553 Y215.843003 Z4 E16959.801402 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.486528 Y214.026444 Z4 E16967.82267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.311428 Y212.28234 Z4 E16975.843937 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.303307 Y210.627489 Z4 E16983.865205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.452614 Y209.077828 Z4 E16991.886473 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.748281 Y207.648281 Z4 E16999.90774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.177828 Y206.352614 Z4 E17007.929008 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.727489 Y205.203307 Z4 E17015.950275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.38234 Y204.211428 Z4 E17023.971543 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X257.126444 Y203.386528 Z4 E17031.992811 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.943003 Y202.736553 Z4 E17040.014078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.814524 Y202.267761 Z4 E17048.035346 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X262.722983 Y201.984668 Z4 E17056.056613 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X264.65 Y201.89 Z4 E17064.077881 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X266.577017 Y201.984668 Z4 E17072.099149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X268.485476 Y202.267761 Z4 E17080.120416 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X269.412624 Y202.5 Z4 E17084.094139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X268.485476 Y202.732239 Z4 E17088.067862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X266.577017 Y203.015332 Z4 E17096.08913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X264.65 Y203.11 Z4 E17104.110397 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X262.722983 Y203.015332 Z4 E17112.131665 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.814524 Y202.732239 Z4 E17120.152933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.943003 Y202.263447 Z4 E17128.1742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X257.126444 Y201.613472 Z4 E17136.195468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.38234 Y200.788572 Z4 E17144.216735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.727489 Y199.796693 Z4 E17152.238003 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.177828 Y198.647386 Z4 E17160.259271 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.748281 Y197.351719 Z4 E17168.280538 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.452614 Y195.922172 Z4 E17176.301806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.303307 Y194.372511 Z4 E17184.323073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.311428 Y192.71766 Z4 E17192.344341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.486528 Y190.973556 Z4 E17200.365609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.836553 Y189.156997 Z4 E17208.386876 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.367761 Y187.285476 Z4 E17216.408144 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.084668 Y185.377017 Z4 E17224.429411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.99 Y183.45 Z4 E17232.450679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.084668 Y181.522983 Z4 E17240.471946 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.367761 Y179.614524 Z4 E17248.493214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.836553 Y177.743003 Z4 E17256.514482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.486528 Y175.926444 Z4 E17264.535749 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.311428 Y174.18234 Z4 E17272.557017 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.303307 Y172.527489 Z4 E17280.578284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.452614 Y170.977828 Z4 E17288.599552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.748281 Y169.548281 Z4 E17296.62082 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.177828 Y168.252614 Z4 E17304.642087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.727489 Y167.103307 Z4 E17312.663355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.38234 Y166.111428 Z4 E17320.684622 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X257.126444 Y165.286528 Z4 E17328.70589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.943003 Y164.636553 Z4 E17336.727158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.814524 Y164.167761 Z4 E17344.748425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X262.722983 Y163.884668 Z4 E17352.769693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X264.65 Y163.79 Z4 E17360.79096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X266.577017 Y163.884668 Z4 E17368.812228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X268.485476 Y164.167761 Z4 E17376.833495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X270.356997 Y164.636553 Z4 E17384.854763 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.173556 Y165.286528 Z4 E17392.876031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X273.91766 Y166.111428 Z4 E17400.897298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.572511 Y167.103307 Z4 E17408.918566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.122172 Y168.252614 Z4 E17416.939833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X278.551719 Y169.548281 Z4 E17424.961101 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X279.847386 Y170.977828 Z4 E17432.982369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X280.996693 Y172.527489 Z4 E17441.003636 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X281.988572 Y174.18234 Z4 E17449.024904 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X282.813472 Y175.926444 Z4 E17457.046171 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.463447 Y177.743003 Z4 E17465.067439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.932239 Y179.614524 Z4 E17473.088706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.215332 Y181.522983 Z4 E17481.109974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.31 Y183.45 Z4 E17489.131242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.215332 Y185.377017 Z4 E17497.152509 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.932239 Y187.285476 Z4 E17505.173777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.463447 Y189.156997 Z4 E17513.195044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X282.813472 Y190.973556 Z4 E17521.216312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X281.988572 Y192.71766 Z4 E17529.23758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X280.996693 Y194.372511 Z4 E17537.258847 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X279.847386 Y195.922172 Z4 E17545.280115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X278.551719 Y197.351719 Z4 E17553.301382 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.122172 Y198.647386 Z4 E17561.32265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.572511 Y199.796693 Z4 E17569.343918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X273.91766 Y200.788572 Z4 E17577.365185 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.173556 Y201.613472 Z4 E17585.386453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X270.356997 Y202.263447 Z4 E17593.40772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X269.412624 Y202.5 Z4 E17597.455265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X270.356997 Y202.736553 Z4 E17601.502809 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.173556 Y203.386528 Z4 E17609.524077 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X273.91766 Y204.211428 Z4 E17617.545344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.572511 Y205.203307 Z4 E17625.566612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.122172 Y206.352614 Z4 E17633.58788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X278.551719 Y207.648281 Z4 E17641.609147 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X279.847386 Y209.077828 Z4 E17649.630415 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X280.996693 Y210.627489 Z4 E17657.651682 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X281.988572 Y212.28234 Z4 E17665.67295 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X282.813472 Y214.026444 Z4 E17673.694218 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.463447 Y215.843003 Z4 E17681.715485 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.932239 Y217.714524 Z4 E17689.736753 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.215332 Y219.622983 Z4 E17697.75802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.31 Y221.55 Z4 E17705.779288 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.215332 Y223.477017 Z4 E17713.800556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.932239 Y225.385476 Z4 E17721.821823 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.463447 Y227.256997 Z4 E17729.843091 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X282.813472 Y229.073556 Z4 E17737.864358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X281.988572 Y230.81766 Z4 E17745.885626 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X280.996693 Y232.472511 Z4 E17753.906893 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X279.847386 Y234.022172 Z4 E17761.928161 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X278.551719 Y235.451719 Z4 E17769.949429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.122172 Y236.747386 Z4 E17777.970696 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.572511 Y237.896693 Z4 E17785.991964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X273.91766 Y238.888572 Z4 E17794.013231 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.173556 Y239.713472 Z4 E17802.034499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X270.356997 Y240.363447 Z4 E17810.055767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X269.412624 Y240.6 Z4 E17814.103311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X270.356997 Y240.836553 Z4 E17818.150856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.173556 Y241.486528 Z4 E17826.172123 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X273.91766 Y242.311428 Z4 E17834.193391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.572511 Y243.303307 Z4 E17842.214658 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.122172 Y244.452614 Z4 E17850.235926 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X278.551719 Y245.748281 Z4 E17858.257193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X279.847386 Y247.177828 Z4 E17866.278461 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X280.996693 Y248.727489 Z4 E17874.299729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X281.988572 Y250.38234 Z4 E17882.320996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X282.813472 Y252.126444 Z4 E17890.342264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.463447 Y253.943003 Z4 E17898.363531 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.932239 Y255.814524 Z4 E17906.384799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.215332 Y257.722983 Z4 E17914.406067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.31 Y259.65 Z4 E17922.427334 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X284.215332 Y261.577017 Z4 E17930.448602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.932239 Y263.485476 Z4 E17938.469869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X283.463447 Y265.356997 Z4 E17946.491137 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X282.813472 Y267.173556 Z4 E17954.512405 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X281.988572 Y268.91766 Z4 E17962.533672 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X280.996693 Y270.572511 Z4 E17970.55494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X279.847386 Y272.122172 Z4 E17978.576207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X278.551719 Y273.551719 Z4 E17986.597475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.122172 Y274.847386 Z4 E17994.618742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.572511 Y275.996693 Z4 E18002.64001 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X273.91766 Y276.988572 Z4 E18010.661278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.173556 Y277.813472 Z4 E18018.682545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X270.356997 Y278.463447 Z4 E18026.703813 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X268.485476 Y278.932239 Z4 E18034.72508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X266.577017 Y279.215332 Z4 E18042.746348 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X264.65 Y279.31 Z4 E18050.767616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X262.722983 Y279.215332 Z4 E18058.788883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.814524 Y278.932239 Z4 E18066.810151 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.943003 Y278.463447 Z4 E18074.831418 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X257.126444 Y277.813472 Z4 E18082.852686 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.38234 Y276.988572 Z4 E18090.873954 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.727489 Y275.996693 Z4 E18098.895221 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.177828 Y274.847386 Z4 E18106.916489 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.748281 Y273.551719 Z4 E18114.937756 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X249.452614 Y272.122172 Z4 E18122.959024 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X248.303307 Y270.572511 Z4 E18130.980291 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.311428 Y268.91766 Z4 E18139.001559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.486528 Y267.173556 Z4 E18147.022827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.836553 Y265.356997 Z4 E18155.044094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.367761 Y263.485476 Z4 E18163.065362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.084668 Y261.577017 Z4 E18171.086629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.99 Y259.65 Z4 E18179.107897 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.084668 Y257.722983 Z4 E18187.129165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.367761 Y255.814524 Z4 E18195.150432 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.6 Y254.887376 Z4 E18199.124155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.832239 Y255.814524 Z4 E18203.097878 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.115332 Y257.722983 Z4 E18211.119146 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.21 Y259.65 Z4 E18219.140414 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X246.115332 Y261.577017 Z4 E18227.161681 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.832239 Y263.485476 Z4 E18235.182949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.363447 Y265.356997 Z4 E18243.204216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X244.713472 Y267.173556 Z4 E18251.225484 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X243.888572 Y268.91766 Z4 E18259.246751 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.896693 Y270.572511 Z4 E18267.268019 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X241.747386 Y272.122172 Z4 E18275.289287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X240.451719 Y273.551719 Z4 E18283.310554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X239.022172 Y274.847386 Z4 E18291.331822 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.472511 Y275.996693 Z4 E18299.353089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X235.81766 Y276.988572 Z4 E18307.374357 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X234.073556 Y277.813472 Z4 E18315.395625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X232.256997 Y278.463447 Z4 E18323.416892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X230.385476 Y278.932239 Z4 E18331.43816 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X228.477017 Y279.215332 Z4 E18339.459427 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X226.55 Y279.31 Z4 E18347.480695 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.622983 Y279.215332 Z4 E18355.501962 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X222.714524 Y278.932239 Z4 E18363.52323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X220.843003 Y278.463447 Z4 E18371.544498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X219.026444 Y277.813472 Z4 E18379.565765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X217.28234 Y276.988572 Z4 E18387.587033 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X215.627489 Y275.996693 Z4 E18395.6083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X214.077828 Y274.847386 Z4 E18403.629568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X212.648281 Y273.551719 Z4 E18411.650836 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X211.352614 Y272.122172 Z4 E18419.672103 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X210.203307 Y270.572511 Z4 E18427.693371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X209.211428 Y268.91766 Z4 E18435.714638 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.386528 Y267.173556 Z4 E18443.735906 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.736553 Y265.356997 Z4 E18451.757174 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.267761 Y263.485476 Z4 E18459.778441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.984668 Y261.577017 Z4 E18467.799709 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.89 Y259.65 Z4 E18475.820976 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.984668 Y257.722983 Z4 E18483.842244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.267761 Y255.814524 Z4 E18491.863511 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.5 Y254.887376 Z4 E18495.837235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.732239 Y255.814524 Z4 E18499.810958 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.015332 Y257.722983 Z4 E18507.832225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.11 Y259.65 Z4 E18515.853493 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X208.015332 Y261.577017 Z4 E18523.87476 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.732239 Y263.485476 Z4 E18531.896028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X207.263447 Y265.356997 Z4 E18539.917296 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X206.613472 Y267.173556 Z4 E18547.938563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X205.788572 Y268.91766 Z4 E18555.959831 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X204.796693 Y270.572511 Z4 E18563.981098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X203.647386 Y272.122172 Z4 E18572.002366 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X202.351719 Y273.551719 Z4 E18580.023634 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X200.922172 Y274.847386 Z4 E18588.044901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X199.372511 Y275.996693 Z4 E18596.066169 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X197.71766 Y276.988572 Z4 E18604.087436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X195.973556 Y277.813472 Z4 E18612.108704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X194.156997 Y278.463447 Z4 E18620.129971 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X192.285476 Y278.932239 Z4 E18628.151239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X190.377017 Y279.215332 Z4 E18636.172507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X188.45 Y279.31 Z4 E18644.193774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X186.522983 Y279.215332 Z4 E18652.215042 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X184.614524 Y278.932239 Z4 E18660.236309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X182.743003 Y278.463447 Z4 E18668.257577 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X180.926444 Y277.813472 Z4 E18676.278845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X179.18234 Y276.988572 Z4 E18684.300112 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X177.527489 Y275.996693 Z4 E18692.32138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X175.977828 Y274.847386 Z4 E18700.342647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X174.548281 Y273.551719 Z4 E18708.363915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X173.252614 Y272.122172 Z4 E18716.385183 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X172.103307 Y270.572511 Z4 E18724.40645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X171.111428 Y268.91766 Z4 E18732.427718 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.286528 Y267.173556 Z4 E18740.448985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.636553 Y265.356997 Z4 E18748.470253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.167761 Y263.485476 Z4 E18756.49152 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.884668 Y261.577017 Z4 E18764.512788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.79 Y259.65 Z4 E18772.534056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.884668 Y257.722983 Z4 E18780.555323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.167761 Y255.814524 Z4 E18788.576591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.4 Y254.887376 Z4 E18792.550314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.632239 Y255.814524 Z4 E18796.524037 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.915332 Y257.722983 Z4 E18804.545305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X170.01 Y259.65 Z4 E18812.566572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.915332 Y261.577017 Z4 E18820.58784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.632239 Y263.485476 Z4 E18828.609107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X169.163447 Y265.356997 Z4 E18836.630375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X168.513472 Y267.173556 Z4 E18844.651643 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X167.688572 Y268.91766 Z4 E18852.67291 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X166.696693 Y270.572511 Z4 E18860.694178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X165.547386 Y272.122172 Z4 E18868.715445 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X164.251719 Y273.551719 Z4 E18876.736713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X162.822172 Y274.847386 Z4 E18884.75798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X161.272511 Y275.996693 Z4 E18892.779248 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X159.61766 Y276.988572 Z4 E18900.800516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X157.873556 Y277.813472 Z4 E18908.821783 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X156.056997 Y278.463447 Z4 E18916.843051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X154.185476 Y278.932239 Z4 E18924.864318 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X152.277017 Y279.215332 Z4 E18932.885586 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X150.35 Y279.31 Z4 E18940.906854 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.422983 Y279.215332 Z4 E18948.928121 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X146.514524 Y278.932239 Z4 E18956.949389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X144.643003 Y278.463447 Z4 E18964.970656 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X142.826444 Y277.813472 Z4 E18972.991924 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X141.08234 Y276.988572 Z4 E18981.013192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X139.427489 Y275.996693 Z4 E18989.034459 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X137.877828 Y274.847386 Z4 E18997.055727 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X136.448281 Y273.551719 Z4 E19005.076994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X135.152614 Y272.122172 Z4 E19013.098262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X134.003307 Y270.572511 Z4 E19021.119529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.011428 Y268.91766 Z4 E19029.140797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X132.186528 Y267.173556 Z4 E19037.162065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.536553 Y265.356997 Z4 E19045.183332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.067761 Y263.485476 Z4 E19053.2046 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.784668 Y261.577017 Z4 E19061.225867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.69 Y259.65 Z4 E19069.247135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.784668 Y257.722983 Z4 E19077.268403 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.067761 Y255.814524 Z4 E19085.28967 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.536553 Y253.943003 Z4 E19093.310938 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X132.186528 Y252.126444 Z4 E19101.332205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.011428 Y250.38234 Z4 E19109.353473 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X134.003307 Y248.727489 Z4 E19117.37474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X135.152614 Y247.177828 Z4 E19125.396008 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X136.448281 Y245.748281 Z4 E19133.417276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X137.877828 Y244.452614 Z4 E19141.438543 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X139.427489 Y243.303307 Z4 E19149.459811 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X141.08234 Y242.311428 Z4 E19157.481078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X142.826444 Y241.486528 Z4 E19165.502346 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X144.643003 Y240.836553 Z4 E19173.523614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X146.514524 Y240.367761 Z4 E19181.544881 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.422983 Y240.084668 Z4 E19189.566149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X150.35 Y239.99 Z4 E19197.587416 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X152.277017 Y240.084668 Z4 E19205.608684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X154.185476 Y240.367761 Z4 E19213.629952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X155.112624 Y240.6 Z4 E19217.603675 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X154.185476 Y240.832239 Z4 E19221.577398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X152.277017 Y241.115332 Z4 E19229.598665 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X150.35 Y241.21 Z4 E19237.619933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.422983 Y241.115332 Z4 E19245.6412 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X146.514524 Y240.832239 Z4 E19253.662468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X144.643003 Y240.363447 Z4 E19261.683736 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X142.826444 Y239.713472 Z4 E19269.705003 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X141.08234 Y238.888572 Z4 E19277.726271 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X139.427489 Y237.896693 Z4 E19285.747538 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X137.877828 Y236.747386 Z4 E19293.768806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X136.448281 Y235.451719 Z4 E19301.790074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X135.152614 Y234.022172 Z4 E19309.811341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X134.003307 Y232.472511 Z4 E19317.832609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.011428 Y230.81766 Z4 E19325.853876 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X132.186528 Y229.073556 Z4 E19333.875144 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.536553 Y227.256997 Z4 E19341.896412 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.067761 Y225.385476 Z4 E19349.917679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.784668 Y223.477017 Z4 E19357.938947 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.69 Y221.55 Z4 E19365.960214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.784668 Y219.622983 Z4 E19373.981482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.067761 Y217.714524 Z4 E19382.002749 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.536553 Y215.843003 Z4 E19390.024017 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X132.186528 Y214.026444 Z4 E19398.045285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.011428 Y212.28234 Z4 E19406.066552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X134.003307 Y210.627489 Z4 E19414.08782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X135.152614 Y209.077828 Z4 E19422.109087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X136.448281 Y207.648281 Z4 E19430.130355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X137.877828 Y206.352614 Z4 E19438.151623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X139.427489 Y205.203307 Z4 E19446.17289 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X141.08234 Y204.211428 Z4 E19454.194158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X142.826444 Y203.386528 Z4 E19462.215425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X144.643003 Y202.736553 Z4 E19470.236693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X146.514524 Y202.267761 Z4 E19478.257961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.422983 Y201.984668 Z4 E19486.279228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X150.35 Y201.89 Z4 E19494.300496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X152.277017 Y201.984668 Z4 E19502.321763 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X154.185476 Y202.267761 Z4 E19510.343031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X155.112624 Y202.5 Z4 E19514.316754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X154.185476 Y202.732239 Z4 E19518.290477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X152.277017 Y203.015332 Z4 E19526.311745 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X150.35 Y203.11 Z4 E19534.333012 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.422983 Y203.015332 Z4 E19542.35428 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X146.514524 Y202.732239 Z4 E19550.375547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X144.643003 Y202.263447 Z4 E19558.396815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X142.826444 Y201.613472 Z4 E19566.418083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X141.08234 Y200.788572 Z4 E19574.43935 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X139.427489 Y199.796693 Z4 E19582.460618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X137.877828 Y198.647386 Z4 E19590.481885 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X136.448281 Y197.351719 Z4 E19598.503153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X135.152614 Y195.922172 Z4 E19606.524421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X134.003307 Y194.372511 Z4 E19614.545688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.011428 Y192.71766 Z4 E19622.566956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X132.186528 Y190.973556 Z4 E19630.588223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.536553 Y189.156997 Z4 E19638.609491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.067761 Y187.285476 Z4 E19646.630758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.784668 Y185.377017 Z4 E19654.652026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.69 Y183.45 Z4 E19662.673294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.784668 Y181.522983 Z4 E19670.694561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.067761 Y179.614524 Z4 E19678.715829 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.536553 Y177.743003 Z4 E19686.737096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X132.186528 Y175.926444 Z4 E19694.758364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.011428 Y174.18234 Z4 E19702.779632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X134.003307 Y172.527489 Z4 E19710.800899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X135.152614 Y170.977828 Z4 E19718.822167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X136.448281 Y169.548281 Z4 E19726.843434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X137.877828 Y168.252614 Z4 E19734.864702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X139.427489 Y167.103307 Z4 E19742.88597 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X141.08234 Y166.111428 Z4 E19750.907237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X142.826444 Y165.286528 Z4 E19758.928505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X144.643003 Y164.636553 Z4 E19766.949772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X146.514524 Y164.167761 Z4 E19774.97104 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.422983 Y163.884668 Z4 E19782.992307 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X150.35 Y163.79 Z4 E19791.013575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X152.277017 Y163.884668 Z4 E19799.034843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X154.185476 Y164.167761 Z4 E19807.05611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X155.112624 Y164.4 Z4 E19811.029833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X154.185476 Y164.632239 Z4 E19815.003556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X152.277017 Y164.915332 Z4 E19823.024824 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X150.35 Y165.01 Z4 E19831.046092 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.422983 Y164.915332 Z4 E19839.067359 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X146.514524 Y164.632239 Z4 E19847.088627 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X144.643003 Y164.163447 Z4 E19855.109894 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X142.826444 Y163.513472 Z4 E19863.131162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X141.08234 Y162.688572 Z4 E19871.15243 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X139.427489 Y161.696693 Z4 E19879.173697 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X137.877828 Y160.547386 Z4 E19887.194965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X136.448281 Y159.251719 Z4 E19895.216232 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X135.152614 Y157.822172 Z4 E19903.2375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X134.003307 Y156.272511 Z4 E19911.258767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.011428 Y154.61766 Z4 E19919.280035 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X132.186528 Y152.873556 Z4 E19927.301303 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.536553 Y151.056997 Z4 E19935.32257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.067761 Y149.185476 Z4 E19943.343838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.784668 Y147.277017 Z4 E19951.365105 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.69 Y145.35 Z4 E19959.386373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X130.784668 Y143.422983 Z4 E19967.407641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.067761 Y141.514524 Z4 E19975.428908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X131.536553 Y139.643003 Z4 E19983.450176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X132.186528 Y137.826444 Z4 E19991.471443 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.011428 Y136.08234 Z4 E19999.492711 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X133.416553 Y135.40643 Z4 E20002.768929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X134.003307 Y134.427489 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X135.152614 Y132.877828 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X136.448281 Y131.448281 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0000
; CLAYLINE_PAGE index=1
G0 X136.448281 Y131.448281 Z8 F2400 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0000 note=inter-page clearance above completed material
G0 X194.5 Y215.5 Z8 F2400 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0000 note=inter-page XY within common stack footprint
G0 X194.5 Y215.5 Z6 F2400 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0000 note=inter-page approach
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-1-rosette-motif page_name=rosette-motif z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X195.458984 Y216.134033 Z6 E20002.952089 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X195.783235 Y216.266775 Z6 E20003.080743 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X196.453125 Y216.541016 Z6 E20003.454298 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X197.216457 Y216.681485 Z6 E20004.016184 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X197.470703 Y216.728271 Z6 E20004.240402 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X198.5 Y216.703125 Z6 E20005.317205 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X198.706772 Y216.656876 Z6 E20005.575253 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X199.529297 Y216.4729 Z6 E20006.72495 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X200.135052 Y216.218129 Z6 E20007.75795 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X200.546875 Y216.044922 Z6 E20008.528584 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X201.441199 Y215.488605 Z6 E20010.564273 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X201.541016 Y215.426514 Z6 E20010.810553 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X202.5 Y214.625 Z6 E20013.665848 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X202.590485 Y214.528048 Z6 E20013.994225 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X203.412109 Y213.647705 Z6 E20017.199042 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X203.588827 Y213.410481 Z6 E20018.047804 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X204.265625 Y212.501953 Z6 E20021.522729 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X204.454328 Y212.187075 Z6 E20022.72501 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X205.048828 Y211.195068 Z6 E20026.756923 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X205.197475 Y210.885404 Z6 E20028.025844 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X205.75 Y209.734375 Z6 E20033.029146 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X205.828918 Y209.525565 Z6 E20033.950306 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X206.357422 Y208.127197 Z6 E20040.165408 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X206.859375 Y206.380859 Z6 E20047.719803 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X207.244141 Y204.502686 Z6 E20055.690514 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X207.5 Y202.5 Z6 E20064.084389 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X207.755859 Y204.502686 Z6 E20072.478263 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X208.140625 Y206.380859 Z6 E20080.448974 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X208.642578 Y208.127197 Z6 E20088.00337 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X209.25 Y209.734375 Z6 E20095.146538 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X209.951172 Y211.195068 Z6 E20101.882827 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X210.734375 Y212.501953 Z6 E20108.217217 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X211.587891 Y213.647705 Z6 E20114.157139 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X212.5 Y214.625 Z6 E20119.71493 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X213.458984 Y215.426514 Z6 E20124.911119 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X214.453125 Y216.044922 Z6 E20129.77869 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X215.470703 Y216.4729 Z6 E20134.36824 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X216.5 Y216.703125 Z6 E20138.753298 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X217.529297 Y216.728271 Z6 E20143.033894 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X218.546875 Y216.541016 Z6 E20147.335528 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X219.541016 Y216.134033 Z6 E20151.801619 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X220.5 Y215.5 Z6 E20156.581225 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.134033 Y214.541016 Z6 E20161.360831 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.541016 Y213.546875 Z6 E20165.826922 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.728271 Y212.529297 Z6 E20170.128556 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.703125 Y211.5 Z6 E20174.409152 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.4729 Y210.470703 Z6 E20178.79421 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.044922 Y209.453125 Z6 E20183.38376 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X220.426514 Y208.458984 Z6 E20188.25133 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X219.625 Y207.5 Z6 E20193.44752 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X218.647705 Y206.587891 Z6 E20199.005311 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X217.501953 Y205.734375 Z6 E20204.945232 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X216.195068 Y204.951172 Z6 E20211.279622 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X214.734375 Y204.25 Z6 E20218.015912 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X213.127197 Y203.642578 Z6 E20225.15908 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X212.683457 Y203.515033 Z6 E20227.078633 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X211.380859 Y203.140625 Z6.677669 E20233.378578 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=6 matz1=6.677669 note=collision lift
G1 X209.502686 Y202.755859 Z7.636259 E20242.290104 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=6.677669 matz1=7.636259 note=collision lift
G1 X208.78107 Y202.663667 Z8 E20245.671614 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=7.636259 matz1=8 note=collision lift
G1 X207.5 Y202.5 Z8 E20251.040974 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X208.739922 Y202.34159 Z8 E20256.23787 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X209.502686 Y202.244141 Z7.615518 E20259.812201 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=7.615518 note=collision lift
G1 X211.380859 Y201.859375 Z6.656928 E20268.723726 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=7.615518 matz1=6.656928 note=collision lift
G1 X212.643589 Y201.496426 Z6 E20274.830851 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=6.656928 matz1=6 note=collision lift
G1 X213.127197 Y201.357422 Z6 E20276.922868 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X214.734375 Y200.75 Z6 E20284.066036 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X216.195068 Y200.048828 Z6 E20290.802326 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X217.501953 Y199.265625 Z6 E20297.136716 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X218.647705 Y198.412109 Z6 E20303.076637 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X219.625 Y197.5 Z6 E20308.634428 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X220.426514 Y196.541016 Z6 E20313.830618 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.044922 Y195.546875 Z6 E20318.698188 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.4729 Y194.529297 Z6 E20323.287738 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.703125 Y193.5 Z6 E20327.672796 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.728271 Y192.470703 Z6 E20331.953392 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.541016 Y191.453125 Z6 E20336.255026 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X221.134033 Y190.458984 Z6 E20340.721117 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X220.5 Y189.5 Z6 E20345.500723 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X219.541016 Y188.865967 Z6 E20350.28033 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X218.546875 Y188.458984 Z6 E20354.746421 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X217.529297 Y188.271729 Z6 E20359.048054 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X216.5 Y188.296875 Z6 E20363.32865 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X215.470703 Y188.5271 Z6 E20367.713708 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X214.453125 Y188.955078 Z6 E20372.303258 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X213.458984 Y189.573486 Z6 E20377.170829 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X212.5 Y190.375 Z6 E20382.367018 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X211.587891 Y191.352295 Z6 E20387.92481 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X210.734375 Y192.498047 Z6 E20393.864731 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X209.951172 Y193.804932 Z6 E20400.199121 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X209.25 Y195.265625 Z6 E20406.935411 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X208.642578 Y196.872803 Z6 E20414.078578 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X208.515033 Y197.316543 Z6 E20415.998132 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X208.140625 Y198.619141 Z7.355338 E20423.967002 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=6 matz1=7.355338 note=collision lift
G1 X207.755859 Y200.497314 Z9.272519 E20435.239289 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=7.355338 matz1=8 note=collision lift
G1 X207.663667 Y201.21893 Z10 E20439.516599 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X207.661039 Y201.239504 Z9.989629 E20439.613009 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X207.65841 Y201.260078 Z10 E20439.709419 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X207.579205 Y201.880039 Z10 E20442.307868 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X207.5 Y202.5 Z10 E20444.906316 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X207.420795 Y201.880039 Z10 E20447.504764 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X207.34159 Y201.260078 Z10 E20450.103212 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X207.244141 Y200.497314 Z9.231037 E20454.624422 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X206.859375 Y198.619141 Z7.313856 E20465.896709 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=7.313856 note=collision lift
G1 X206.496426 Y197.356411 Z6 E20473.621679 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=7.313856 matz1=6 note=collision lift
G1 X206.357422 Y196.872803 Z6 E20475.713696 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X205.75 Y195.265625 Z6 E20482.856864 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X205.048828 Y193.804932 Z6 E20489.593154 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X204.265625 Y192.498047 Z6 E20495.927544 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X203.412109 Y191.352295 Z6 E20501.867465 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X202.5 Y190.375 Z6 E20507.425256 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X201.541016 Y189.573486 Z6 E20512.621446 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X200.546875 Y188.955078 Z6 E20517.489016 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X199.529297 Y188.5271 Z6 E20522.078566 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X198.5 Y188.296875 Z6 E20526.463624 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X197.470703 Y188.271729 Z6 E20530.74422 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X196.453125 Y188.458984 Z6 E20535.045854 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X195.458984 Y188.865967 Z6 E20539.511945 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X194.5 Y189.5 Z6 E20544.291551 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.865967 Y190.458984 Z6 E20549.071157 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.458984 Y191.453125 Z6 E20553.537248 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.271729 Y192.470703 Z6 E20557.838882 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.296875 Y193.5 Z6 E20562.119478 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.5271 Y194.529297 Z6 E20566.504536 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.955078 Y195.546875 Z6 E20571.094086 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X194.573486 Y196.541016 Z6 E20575.961656 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X195.375 Y197.5 Z6 E20581.157846 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X196.352295 Y198.412109 Z6 E20586.715637 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X197.498047 Y199.265625 Z6 E20592.655559 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X198.804932 Y200.048828 Z6 E20598.989949 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X200.265625 Y200.75 Z6 E20605.726238 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X201.872803 Y201.357422 Z6 E20612.869406 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X202.316543 Y201.484967 Z6 E20614.78896 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X203.619141 Y201.859375 Z7.355338 E20622.75783 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=6 matz1=7.355338 note=collision lift
G1 X205.497314 Y202.244141 Z9.272519 E20634.030117 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=7.355338 matz1=8 note=collision lift
G1 X206.21893 Y202.336333 Z10 E20638.307427 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X206.239504 Y202.338961 Z9.989629 E20638.403837 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X206.260078 Y202.34159 Z10 E20638.500247 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X206.880039 Y202.420795 Z10 E20641.098695 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X207.5 Y202.5 Z10 E20643.697143 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X206.880039 Y202.579205 Z10 E20646.295591 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X206.260078 Y202.65841 Z10 E20648.894039 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X206.21893 Y202.663667 Z9.979259 E20649.08686 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X205.497314 Y202.755859 Z9.251778 E20653.36417 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=8 note=collision lift
G1 X203.619141 Y203.140625 Z7.334597 E20664.636457 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=8 matz1=7.334597 note=collision lift
G1 X202.356411 Y203.503574 Z6.020741 E20672.361426 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=7.334597 matz1=6.020741 note=collision lift
G1 X202.316543 Y203.515033 Z6 E20672.554247 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 matz0=6.020741 matz1=6 note=collision lift
G1 X201.872803 Y203.642578 Z6 E20674.4738 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X200.265625 Y204.25 Z6 E20681.616968 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X198.804932 Y204.951172 Z6 E20688.353258 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X197.498047 Y205.734375 Z6 E20694.687648 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X196.352295 Y206.587891 Z6 E20700.627569 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X195.375 Y207.5 Z6 E20706.18536 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X194.573486 Y208.458984 Z6 E20711.38155 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.955078 Y209.453125 Z6 E20716.24912 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.5271 Y210.470703 Z6 E20720.83867 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.452263 Y210.805285 Z6 E20722.264071 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X193.296875 Y211.5 Z6 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=end-early tail
G1 X193.271729 Y212.529297 Z6 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=end-early tail
G1 X193.458984 Y213.546875 Z6 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=end-early tail
G1 X193.865967 Y214.541016 Z6 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=end-early tail
G1 X194.5 Y215.5 Z6 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
; CLAYLINE_MARKER page=1 layer=1 text=layer 1 page_id=page-1-rosette-motif page_name=rosette-motif z_mode=calibrated
G0 X194.5 Y215.5 Z8 F2400 ; clayline kind=travel_approach page=1 layer=1 stroke=stroke-0000 note=vertical layer transition
; CLAYLINE_STROKE_BEGIN page=1 layer=1 id=stroke-0000
G1 X193.865967 Y214.541016 Z8 E20722.44723 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.733225 Y214.216765 Z8 E20722.575885 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.458984 Y213.546875 Z8 E20722.949439 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.318515 Y212.783543 Z8 E20723.511326 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.271729 Y212.529297 Z8 E20723.735544 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.296875 Y211.5 Z8 E20724.812347 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.343124 Y211.293228 Z8 E20725.070395 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.5271 Y210.470703 Z8 E20726.220092 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.781871 Y209.864948 Z8 E20727.253091 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X193.955078 Y209.453125 Z8 E20728.023726 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X194.511395 Y208.558801 Z8 E20730.059415 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X194.573486 Y208.458984 Z8 E20730.305694 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X195.375 Y207.5 Z8 E20733.16099 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X195.471952 Y207.409515 Z8 E20733.489366 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X196.352295 Y206.587891 Z8 E20736.694183 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X196.589519 Y206.411173 Z8 E20737.542945 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X197.498047 Y205.734375 Z8 E20741.017871 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X197.812925 Y205.545672 Z8 E20742.220152 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X198.791116 Y204.959451 Z8 E20746.193368 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=prime ramp
G1 X198.804932 Y204.951172 Z8.008053 E20746.258998 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8 matz1=8.008053 note=collision lift
G1 X199.080371 Y204.818954 Z8.160818 E20747.520986 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.008053 matz1=8.160818 note=collision lift
G1 X200.265625 Y204.25 Z8.818187 E20753.320522 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.160818 matz1=8.818187 note=collision lift
G1 X200.29079 Y204.240489 Z8.831638 E20753.445447 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.818187 matz1=8.831638 note=collision lift
G1 X201.232409 Y203.88461 Z9.334951 E20758.124492 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.831638 matz1=9.334951 note=collision lift
G1 X201.232572 Y203.884549 Z9.334864 E20758.1253 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.334951 matz1=9.334864 note=collision lift
G1 X201.872803 Y203.642578 Z9.572361 E20761.137277 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.334864 matz1=9.572361 note=collision lift
G1 X201.872855 Y203.642563 Z9.572334 E20761.137531 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.572361 matz1=9.572334 note=collision lift
G1 X203.057698 Y203.302002 Z10.00016 E20766.562842 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.572334 matz1=10 note=collision lift
G1 X203.058005 Y203.301913 Z10 E20766.564326 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.203742 Y203.260024 Z10 E20767.194763 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.211974 Y203.257658 Z10.003679 E20767.233518 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.219046 Y203.255625 Z10 E20767.267723 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.619141 Y203.140625 Z10 E20768.998473 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X205.497314 Y202.755859 Z10 E20776.969184 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.5 Y202.5 Z10 E20785.363058 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X205.497314 Y202.244141 Z10 E20793.756933 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.619141 Y201.859375 Z10 E20801.727644 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.219273 Y201.74444 Z10 E20803.45741 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.211974 Y201.742342 Z10.003798 E20803.492715 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.203742 Y201.739976 Z10 E20803.531667 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.057995 Y201.698084 Z10 E20804.162145 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X203.057698 Y201.697998 Z10.000155 E20804.163583 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X201.872854 Y201.357437 Z9.585664 E20809.570975 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=9.585664 note=collision lift
G1 X201.872803 Y201.357422 Z9.585691 E20809.571224 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.585664 matz1=9.585691 note=collision lift
G1 X201.232582 Y201.115455 Z9.355601 E20812.573208 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.585691 matz1=9.355601 note=collision lift
G1 X201.232409 Y201.11539 Z9.355693 E20812.574063 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.355601 matz1=9.355693 note=collision lift
G1 X200.265625 Y200.75 Z8.838928 E20817.378158 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.355693 matz1=8.838928 note=collision lift
G1 X198.804932 Y200.048828 Z8.028794 E20824.909559 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.838928 matz1=8.028794 note=collision lift
G1 X198.755534 Y200.019225 Z8 E20825.177246 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.028794 matz1=8 note=collision lift
G1 X197.498047 Y199.265625 Z8 E20831.27221 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X196.352295 Y198.412109 Z8 E20837.212131 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X195.375 Y197.5 Z8 E20842.769922 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X194.573486 Y196.541016 Z8 E20847.966112 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X193.955078 Y195.546875 Z8 E20852.833682 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X193.5271 Y194.529297 Z8 E20857.423232 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X193.296875 Y193.5 Z8 E20861.80829 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X193.271729 Y192.470703 Z8 E20866.088886 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X193.458984 Y191.453125 Z8 E20870.39052 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X193.865967 Y190.458984 Z8 E20874.856611 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X194.5 Y189.5 Z8 E20879.636217 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X195.458984 Y188.865967 Z8 E20884.415823 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X196.453125 Y188.458984 Z8 E20888.881914 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X197.470703 Y188.271729 Z8 E20893.183548 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X198.5 Y188.296875 Z8 E20897.464144 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X199.529297 Y188.5271 Z8 E20901.849202 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X200.546875 Y188.955078 Z8 E20906.438752 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X201.541016 Y189.573486 Z8 E20911.306322 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X202.5 Y190.375 Z8 E20916.502512 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X203.412109 Y191.352295 Z8 E20922.060303 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X204.265625 Y192.498047 Z8 E20928.000224 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X205.048828 Y193.804932 Z8 E20934.334614 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X205.05981 Y193.827808 Z8 E20934.440116 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X205.75 Y195.265625 Z8.797446 E20941.853563 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8 matz1=8.797446 note=collision lift
G1 X206.11539 Y196.232409 Z9.31421 E20946.657658 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.797446 matz1=9.31421 note=collision lift
G1 X206.115448 Y196.232563 Z9.314128 E20946.658421 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.31421 matz1=9.314128 note=collision lift
G1 X206.357422 Y196.872803 Z9.559031 E20949.68067 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.314128 matz1=9.559031 note=collision lift
G1 X206.357437 Y196.872856 Z9.559004 E20949.680929 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.559031 matz1=9.559004 note=collision lift
G1 X206.484967 Y197.316543 Z9.724205 E20951.71944 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.559004 matz1=9.724205 note=collision lift
G1 X206.697998 Y198.057698 Z10.385746 E20955.94363 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.724205 matz1=10 note=collision lift
G1 X206.698089 Y198.058014 Z10.385746 E20955.944998 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X206.739976 Y198.203742 Z10.46156 E20956.649802 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X206.742342 Y198.211974 Z10.469522 E20956.69842 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X206.744375 Y198.219046 Z10.469522 E20956.729013 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X206.859375 Y198.619141 Z10.677669 E20958.664051 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.244141 Y200.497314 Z11.636259 E20967.575576 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.336333 Y201.21893 Z12 E20970.957086 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.338961 Y201.239504 Z11.989629 E20971.053497 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.34159 Y201.260078 Z12 E20971.149907 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.420795 Y201.880039 Z12 E20973.748355 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.5 Y202.5 Z12 E20976.346803 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.579205 Y201.880039 Z12 E20978.945251 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.65841 Y201.260078 Z12 E20981.543699 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.755859 Y200.497314 Z11.615518 E20985.11803 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.140625 Y198.619141 Z10.656928 E20994.029555 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.255494 Y198.219501 Z10.449018 E20995.962392 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.257658 Y198.211974 Z10.449018 E20995.994954 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.260024 Y198.203742 Z10.440819 E20996.044247 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.301916 Y198.057995 Z10.364995 E20996.749143 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.302002 Y198.057698 Z10.364995 E20996.750429 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.503574 Y197.356411 Z9.754826 E21000.704972 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=9.754826 note=collision lift
G1 X208.642563 Y196.872854 Z9.585664 E21002.91183 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.754826 matz1=9.585664 note=collision lift
G1 X208.642578 Y196.872803 Z9.585691 E21002.912079 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.585664 matz1=9.585691 note=collision lift
G1 X208.884545 Y196.232582 Z9.355601 E21005.914063 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.585691 matz1=9.355601 note=collision lift
G1 X208.88461 Y196.232409 Z9.355693 E21005.914918 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.355601 matz1=9.355693 note=collision lift
G1 X209.25 Y195.265625 Z8.838928 E21010.719013 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.355693 matz1=8.838928 note=collision lift
G1 X209.951172 Y193.804932 Z8.028794 E21018.250414 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.838928 matz1=8.028794 note=collision lift
G1 X209.980775 Y193.755534 Z8 E21018.518101 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.028794 matz1=8 note=collision lift
G1 X210.734375 Y192.498047 Z8 E21024.613064 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X211.587891 Y191.352295 Z8 E21030.552985 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X212.5 Y190.375 Z8 E21036.110777 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X213.458984 Y189.573486 Z8 E21041.306966 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X214.453125 Y188.955078 Z8 E21046.174537 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X215.470703 Y188.5271 Z8 E21050.764087 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X216.5 Y188.296875 Z8 E21055.149145 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X217.529297 Y188.271729 Z8 E21059.429741 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X218.546875 Y188.458984 Z8 E21063.731374 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X219.541016 Y188.865967 Z8 E21068.197465 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X220.5 Y189.5 Z8 E21072.977072 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.134033 Y190.458984 Z8 E21077.756678 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.541016 Y191.453125 Z8 E21082.222769 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.728271 Y192.470703 Z8 E21086.524403 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.703125 Y193.5 Z8 E21090.804999 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.4729 Y194.529297 Z8 E21095.190056 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.044922 Y195.546875 Z8 E21099.779606 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X220.426514 Y196.541016 Z8 E21104.647177 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X219.625 Y197.5 Z8 E21109.843366 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X218.647705 Y198.412109 Z8 E21115.401158 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X217.501953 Y199.265625 Z8 E21121.341079 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X216.195068 Y200.048828 Z8 E21127.675469 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X214.988102 Y200.628204 Z8 E21133.241643 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X214.988002 Y200.628252 Z8.000055 E21133.242159 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8 matz1=8.000055 note=collision lift
G1 X214.836016 Y200.701209 Z8.084089 E21134.025319 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.000055 matz1=8.084089 note=collision lift
G1 X214.734375 Y200.75 Z8.140462 E21134.549387 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.084089 matz1=8.140462 note=collision lift
G1 X213.767591 Y201.11539 Z8.657226 E21139.353482 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.140462 matz1=8.657226 note=collision lift
G1 X213.127197 Y201.357422 Z8.999455 E21142.535555 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.657226 matz1=8.999455 note=collision lift
G1 X213.127133 Y201.35744 Z8.999422 E21142.535865 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.999455 matz1=8.999422 note=collision lift
G1 X212.683457 Y201.484967 Z9.230214 E21144.681629 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.999422 matz1=9.230214 note=collision lift
G1 X211.942302 Y201.697998 Z10.00133 E21149.215637 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.230214 matz1=10 note=collision lift
G1 X211.942273 Y201.698007 Z10.00133 E21149.215763 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.380859 Y201.859375 Z10.585426 E21152.650165 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.380786 Y201.85939 Z10.585426 E21152.650477 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.19997 Y201.896432 Z10.769997 E21153.735687 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.19996 Y201.896434 Z10.769997 E21153.735727 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.163212 Y201.903963 Z10.788753 E21153.910089 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.162867 Y201.904033 Z10.789105 E21153.912161 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.162521 Y201.904104 Z10.789105 E21153.913627 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X209.502686 Y202.244141 Z11.636259 E21161.789186 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.78107 Y202.336333 Z12 E21165.170696 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.760496 Y202.338961 Z11.989629 E21165.267107 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.739922 Y202.34159 Z12 E21165.363517 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.119961 Y202.420795 Z12 E21167.961965 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.5 Y202.5 Z12 E21170.560413 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.119961 Y202.579205 Z12 E21173.158861 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X208.739922 Y202.65841 Z12 E21175.757309 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X209.502686 Y202.755859 Z11.615518 E21179.33164 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.12531 Y203.088273 Z10.787356 E21187.030639 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.12578 Y203.088369 Z10.787356 E21187.032636 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.126251 Y203.088465 Z10.786876 E21187.035458 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.240556 Y203.111882 Z10.728536 E21187.577814 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.240562 Y203.111883 Z10.728536 E21187.577838 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.380761 Y203.140605 Z10.585426 E21188.419274 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.380859 Y203.140625 Z10.585426 E21188.419691 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.942273 Y203.301993 Z10.00133 E21191.854094 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X211.942302 Y203.302002 Z10.00133 E21191.85422 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X212.643589 Y203.503574 Z9.271693 E21196.144334 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=9.271693 note=collision lift
G1 X213.127133 Y203.64256 Z9.020163 E21198.482914 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.271693 matz1=9.020163 note=collision lift
G1 X213.127197 Y203.642578 Z9.020196 E21198.483224 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.020163 matz1=9.020196 note=collision lift
G1 X213.767591 Y203.88461 Z8.677967 E21201.665297 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=9.020196 matz1=8.677967 note=collision lift
G1 X214.734375 Y204.25 Z8.161203 E21206.469392 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.677967 matz1=8.161203 note=collision lift
G1 X214.833211 Y204.297444 Z8.106386 E21206.978996 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.161203 matz1=8.106386 note=collision lift
G1 X215.025447 Y204.389722 Z8.000073 E21207.969606 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.106386 matz1=8.000073 note=collision lift
G1 X215.025579 Y204.389786 Z8 E21207.970286 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.000073 matz1=8 note=collision lift
G1 X216.195068 Y204.951172 Z8 E21213.363628 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X217.501953 Y205.734375 Z8 E21219.698018 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X218.647705 Y206.587891 Z8 E21225.637939 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X219.625 Y207.5 Z8 E21231.19573 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X220.426514 Y208.458984 Z8 E21236.39192 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.044922 Y209.453125 Z8 E21241.25949 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.4729 Y210.470703 Z8 E21245.84904 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.703125 Y211.5 Z8 E21250.234098 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.728271 Y212.529297 Z8 E21254.514694 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.541016 Y213.546875 Z8 E21258.816328 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X221.134033 Y214.541016 Z8 E21263.282419 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X220.5 Y215.5 Z8 E21268.062025 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X219.541016 Y216.134033 Z8 E21272.841631 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X218.546875 Y216.541016 Z8 E21277.307722 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X217.529297 Y216.728271 Z8 E21281.609356 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X216.5 Y216.703125 Z8 E21285.889952 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X215.470703 Y216.4729 Z8 E21290.27501 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X214.453125 Y216.044922 Z8 E21294.86456 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X213.458984 Y215.426514 Z8 E21299.73213 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X212.5 Y214.625 Z8 E21304.92832 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X211.587891 Y213.647705 Z8 E21310.486111 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X210.734375 Y212.501953 Z8 E21316.426032 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X209.951172 Y211.195068 Z8 E21322.760422 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X209.25 Y209.734375 Z8 E21329.496712 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X208.940476 Y208.915405 Z8 E21333.136656 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X208.642578 Y208.127197 Z8.421312 E21337.053379 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8 matz1=8.421312 note=collision lift
G1 X208.515033 Y207.683457 Z8.652165 E21339.199506 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.421312 matz1=8.652165 note=collision lift
G1 X208.140625 Y206.380859 Z10.007504 E21347.168376 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.652165 matz1=10 note=collision lift
G1 X207.871629 Y205.067799 Z11.347835 E21355.049008 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.755859 Y204.502686 Z11.636259 E21357.730347 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.663667 Y203.78107 Z12 E21361.111857 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.661039 Y203.760496 Z11.989629 E21361.208267 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.65841 Y203.739922 Z12 E21361.304677 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.579205 Y203.119961 Z12 E21363.903125 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.5 Y202.5 Z12 E21366.501573 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.420795 Y203.119961 Z12 E21369.100021 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.34159 Y203.739922 Z12 E21371.69847 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.338961 Y203.760496 Z11.989629 E21371.79488 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.336333 Y203.78107 Z12 E21371.89129 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.244141 Y204.502686 Z11.636259 E21375.2728 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X207.128371 Y205.067799 Z11.347835 E21377.954139 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X206.859375 Y206.380859 Z10.007504 E21385.834771 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=10 note=collision lift
G1 X206.484967 Y207.683457 Z8.652165 E21393.803641 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=10 matz1=8.652165 note=collision lift
G1 X206.357422 Y208.127197 Z8.421312 E21395.949767 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.652165 matz1=8.421312 note=collision lift
G1 X206.059524 Y208.915405 Z8 E21399.86649 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 matz0=8.421312 matz1=8 note=collision lift
G1 X205.75 Y209.734375 Z8 E21403.506435 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X205.048828 Y211.195068 Z8 E21410.242724 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X204.265625 Y212.501953 Z8 E21416.577114 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X203.412109 Y213.647705 Z8 E21422.517036 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X202.5 Y214.625 Z8 E21428.074827 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X201.541016 Y215.426514 Z8 E21433.271016 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X200.546875 Y216.044922 Z8 E21438.138587 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X199.529297 Y216.4729 Z8 E21442.728137 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X199.194715 Y216.547737 Z8 E21444.153537 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X198.5 Y216.703125 Z8 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=end-early tail
G1 X197.470703 Y216.728271 Z8 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=end-early tail
G1 X196.453125 Y216.541016 Z8 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=end-early tail
G1 X195.458984 Y216.134033 Z8 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=end-early tail
G1 X194.5 Y215.5 Z8 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=1 id=stroke-0000
; CLAYLINE_BODY_END
; CLAYLINE_PROFILE_END_BEGIN
M83 ;Set to Relative Extrusion Mode
G91 ;Set to Relative Positioning
G1 Z150 E-100 F40000 ;Move Z Axis up and relieve Extruder pressure (v1.3.0: was E-3000, which left the next job dry)
G90 ;Set to Absolute Positioning
G28 Z ;Home Z
G1 X207.5 Y0 F500 ;Move X and Y slow to home position
M82 ;absolute extrusion mode
; CLAYLINE_PROFILE_END_END
