; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=pages-job-page-03-petal-flower
; prepared_trace_sha256=d9343388c73339303a9877a86c68a301f218681cb5ef0e522aca2c66b0373b77
; body_sha256=b9cfc959816b45337c3cf3e733ae8426b6379006f0d6765198502f9ef958649b
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
; stats.motion_count=6698
; stats.print_motion_count=6431
; stats.travel_motion_count=267
; stats.stroke_count=90
; stats.page_count=1
; stats.print_path_mm=6338.067786
; stats.deposited_path_mm=5888.067786
; stats.travel_path_mm=2117.763583
; stats.total_motion_path_mm=8455.831369
; stats.motion_time_seconds=237.585454
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=237.585454
; stats.body_volume_mm3=54710.938178
; stats.wet_weight_g=98.479689
; stats.body_e=22746.164904
; stats.pressure_e_excluded=0
; stats.warning_count=143
; nominal_label=calibrated centerline
; stats.warning_count.open_end=2
; stats.warning_count.tight_radius=32
; stats.warning_count.under_spaced=109
; parameter.alternate=true
; parameter.first_layer_flow_factor=1.1
; parameter.first_layer_speed_factor=0.6
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.joint_boost=0.0
; parameter.layers=2
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_pause_seconds=disabled
; parameter.page_travel_clearance=50
; parameter.provisional_flow_multiplier=1.0
; parameter.split_source_page=3
; parameter.standoff_z=20.0
; parameter.z_mode=calibrated
; parameter.z_modulation=0.0
; parameter.z_step_per_layer=2
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-2-petal-flower-1 page_name=petal-flower z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X188.775343 Y182.403343 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start XY at safe Z
G0 X188.775343 Y182.403343 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0000 note=stroke start vertical approach
G1 X189.493495 Y181.610984 Z2 E0.174329 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X189.750014 Y181.265107 Z2 E0.342995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X190.130524 Y180.752049 Z2 E0.697317 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X190.573289 Y180.01334 Z2 E1.371981 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X190.680296 Y179.83481 Z2 E1.568963 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.137515 Y178.868101 Z2 E2.789268 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.212465 Y178.65863 Z2 E3.086956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.497779 Y177.861232 Z2 E4.358232 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.656468 Y177.227709 Z2 E5.487922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.757617 Y176.823899 Z2 E6.275853 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.914528 Y175.766093 Z2 E8.542134 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.915231 Y175.751776 Z2 E8.574879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.967 Y174.698 Z2 E11.157073 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.945167 Y174.253583 Z2 E12.347825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.914528 Y173.629907 Z2 E14.12067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.786055 Y172.763812 Z2 E16.806762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.757617 Y172.572101 Z2 E17.432926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.497779 Y171.534768 Z2 E21.093841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.418 Y171.311801 Z2 E21.951689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X191.137515 Y170.527899 Z2 E25.103414 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X190.852152 Y169.92455 Z2 E27.782607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X190.680296 Y169.56119 Z2 E29.461645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X190.130524 Y168.643951 Z2 E34.168535 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X190.113447 Y168.620925 Z2 E34.299514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X189.493495 Y167.785016 Z2 E39.058976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.775343 Y166.992657 Z2 E43.949542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.982984 Y166.274505 Z2 E48.840108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.124049 Y165.637476 Z2 E53.730674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.20681 Y165.087704 Z2 E58.62124 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X185.240101 Y164.630485 Z2 E63.511806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.233232 Y164.270221 Z2 E68.402372 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X183.195899 Y164.010383 Z2 E73.292938 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.138093 Y163.853472 Z2 E78.183504 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X181.07 Y163.801 Z2 E83.074071 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.001907 Y163.853472 Z2 E87.964637 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X178.944101 Y164.010383 Z2 E92.855203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.906768 Y164.270221 Z2 E97.745769 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.899899 Y164.630485 Z2 E102.636335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.93319 Y165.087704 Z2 E107.526901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.015951 Y165.637476 Z2 E112.417467 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.157016 Y166.274505 Z2 E117.308033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.364657 Y166.992657 Z2 E122.198599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.646505 Y167.785016 Z2 E127.089165 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.009476 Y168.643951 Z2 E131.979731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.459704 Y169.56119 Z2 E136.870297 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.002485 Y170.527899 Z2 E141.760863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.642221 Y171.534768 Z2 E146.651429 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.382383 Y172.572101 Z2 E151.541995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.225472 Y173.629907 Z2 E156.432561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.173 Y174.698 Z2 E161.323127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.225472 Y175.766093 Z2 E166.213693 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.382383 Y176.823899 Z2 E171.104259 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.642221 Y177.861232 Z2 E175.994825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.002485 Y178.868101 Z2 E180.885391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.459704 Y179.83481 Z2 E185.775957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.009476 Y180.752049 Z2 E190.666523 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.646505 Y181.610984 Z2 E195.557089 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.364657 Y182.403343 Z2 E200.447655 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.157016 Y183.121495 Z2 E205.338221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.015951 Y183.758524 Z2 E210.228787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.93319 Y184.308296 Z2 E215.119353 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.899899 Y184.765515 Z2 E220.009919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.906768 Y185.125779 Z2 E224.900485 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X178.944101 Y185.385617 Z2 E229.791051 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.001907 Y185.542528 Z2 E234.681617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X181.07 Y185.595 Z2 E239.572184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.138093 Y185.542528 Z2 E244.46275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X183.195899 Y185.385617 Z2 E249.353316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.233232 Y185.125779 Z2 E254.243882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X184.559858 Y185.00891 Z2 E255.830369 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X185.240101 Y184.765515 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X186.20681 Y184.308296 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X187.124049 Y183.758524 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X187.982984 Y183.121495 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X188.775343 Y182.403343 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G0 X188.775343 Y182.403343 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0001 note=intra-page lift
G0 X184.119993 Y163.818144 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0001 note=intra-page XY
G0 X184.119993 Y163.818144 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X184.233232 Y163.789779 Z2 E255.832446 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X185.240101 Y163.429515 Z2 E256.044837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X185.523847 Y163.295314 Z2 E256.173364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X186.20681 Y162.972296 Z2 E256.605885 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X186.845389 Y162.589546 Z2 E257.20235 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X187.124049 Y162.422524 Z2 E257.515593 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X187.982984 Y161.785495 Z2 E258.773959 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X188.061331 Y161.714485 Z2 E258.917325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X188.775343 Y161.067343 Z2 E260.380983 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.135538 Y160.669928 Z2 E261.318291 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.493495 Y160.274984 Z2 E262.336666 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X190.069522 Y159.498301 Z2 E264.405248 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X190.130524 Y159.416049 Z2 E264.641007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X190.680296 Y158.49881 Z2 E267.294007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X190.820626 Y158.202108 Z2 E268.178194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.137515 Y157.532101 Z2 E270.295665 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.393159 Y156.817626 Z2 E272.637131 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.497779 Y156.525232 Z2 E273.645982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.757617 Y155.487899 Z2 E277.344958 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.775235 Y155.369127 Z2 E277.782058 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.914528 Y154.430093 Z2 E281.392592 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.941549 Y153.880065 Z2 E283.612975 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.967 Y153.362 Z2 E285.788885 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.918849 Y152.381872 Z2 E290.129883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X191.914528 Y152.293907 Z2 E290.532653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X191.757617 Y151.236101 Z2 E295.423219 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X191.497779 Y150.198768 Z2 E300.313785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X191.137515 Y149.191899 Z2 E305.204351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X190.680296 Y148.22519 Z2 E310.094917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X190.130524 Y147.307951 Z2 E314.985483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X189.493495 Y146.449016 Z2 E319.876049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X188.775343 Y145.656657 Z2 E324.766615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X187.982984 Y144.938505 Z2 E329.657181 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X187.124049 Y144.301476 Z2 E334.547747 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X186.20681 Y143.751704 Z2 E339.438313 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X185.240101 Y143.294485 Z2 E344.32888 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X184.233232 Y142.934221 Z2 E349.219446 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X183.195899 Y142.674383 Z2 E354.110012 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X182.138093 Y142.517472 Z2 E359.000578 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X181.07 Y142.465 Z2 E363.891144 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X180.001907 Y142.517472 Z2 E368.78171 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X178.944101 Y142.674383 Z2 E373.672276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X177.906768 Y142.934221 Z2 E378.562842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X176.899899 Y143.294485 Z2 E383.453408 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X175.93319 Y143.751704 Z2 E388.343974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X175.015951 Y144.301476 Z2 E393.23454 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X174.157016 Y144.938505 Z2 E398.125106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X173.364657 Y145.656657 Z2 E403.015672 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X172.646505 Y146.449016 Z2 E407.906238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X172.009476 Y147.307951 Z2 E412.796804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X171.459704 Y148.22519 Z2 E417.68737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X171.002485 Y149.191899 Z2 E422.577936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X170.642221 Y150.198768 Z2 E427.468502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X170.382383 Y151.236101 Z2 E432.359068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X170.225472 Y152.293907 Z2 E437.249634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X170.173 Y153.362 Z2 E442.1402 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X170.225472 Y154.430093 Z2 E447.030766 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X170.382383 Y155.487899 Z2 E451.921332 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X170.642221 Y156.525232 Z2 E456.811898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X171.002485 Y157.532101 Z2 E461.702464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X171.459704 Y158.49881 Z2 E466.59303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X172.009476 Y159.416049 Z2 E471.483596 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X172.646505 Y160.274984 Z2 E476.374162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X173.364657 Y161.067343 Z2 E481.264728 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X174.157016 Y161.785495 Z2 E486.155294 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X174.379925 Y161.950816 Z2 E487.424484 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X175.015951 Y162.422524 Z2.395929 E491.473306 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2 matz1=2.395929 note=collision lift
G1 X175.93319 Y162.972296 Z2.930619 E496.941125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X176.899899 Y163.429515 Z3.46531 E502.408944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X177.906768 Y163.789779 Z4 E507.876763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=3.46531 matz1=4 note=collision lift
G1 X178.944101 Y164.049617 Z4 E512.767329 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=4 matz1=4 note=collision lift
G1 X179.56546 Y164.141787 Z3.685921 E515.979147 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=4 matz1=3.685921 note=collision lift
G1 X180.001907 Y164.206528 Z3.46531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=3.685921 matz1=3.46531 note=collision lift
G1 X181.07 Y164.259 Z2.930619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X182.138093 Y164.206528 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X182.921379 Y164.090338 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.395929 matz1=2 note=collision lift
G1 X183.195899 Y164.049617 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
G1 X184.119993 Y163.818144 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
G0 X184.119993 Y163.818144 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0002 note=intra-page lift
G0 X169.440962 Y158.945048 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0002 note=intra-page XY
G0 X169.440962 Y158.945048 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0002
G1 X169.874584 Y157.515588 Z2 E516.319304 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X169.875193 Y157.509399 Z2 E516.322142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X170.021 Y156.029 Z2 E517.339775 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X170.019781 Y156.016622 Z2 E517.351127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X169.874584 Y154.542412 Z2 E519.04056 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X169.869168 Y154.524559 Z2 E519.066103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X169.440962 Y153.112952 Z2 E521.421659 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X169.429236 Y153.091014 Z2 E521.467069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X168.736798 Y151.795555 Z2 E524.483072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X168.717073 Y151.771519 Z2 E524.554025 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X167.789154 Y150.640846 Z2 E528.2248 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X167.760311 Y150.617175 Z2 E528.326972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X166.634445 Y149.693202 Z2 E532.646841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X166.596054 Y149.672681 Z2 E532.785909 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X165.317048 Y148.989038 Z2 E537.749196 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X165.26944 Y148.974596 Z2 E537.930836 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X163.887588 Y148.555416 Z2 E543.531866 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X163.831889 Y148.54993 Z2 E543.761753 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X162.401 Y148.409 Z2 E549.994849 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X162.339112 Y148.415095 Z2 E550.278661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X160.914412 Y148.555416 Z2 E556.825722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X159.484952 Y148.989038 Z2 E563.657185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X158.167555 Y149.693202 Z2 E570.488648 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X157.012846 Y150.640846 Z2 E577.32011 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X156.065202 Y151.795555 Z2 E584.151573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X155.361038 Y153.112952 Z2 E590.983036 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X154.927416 Y154.542412 Z2 E597.814498 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X154.781 Y156.029 Z2 E604.645961 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X154.927416 Y157.515588 Z2 E611.477424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X155.361038 Y158.945048 Z2 E618.308887 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X156.065202 Y160.262445 Z2 E625.140349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X157.012846 Y161.417154 Z2 E631.971812 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X158.167555 Y162.364798 Z2 E638.803275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X159.484952 Y163.068962 Z2 E645.634737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X160.914412 Y163.502584 Z2 E652.4662 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X162.401 Y163.649 Z2 E659.297663 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X163.887588 Y163.502584 Z2 E666.129125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X165.317048 Y163.068962 Z2 E672.960588 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X166.177031 Y162.609291 Z2 E677.420096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X166.634445 Y162.364798 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X167.789154 Y161.417154 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X168.736798 Y160.262445 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X169.440962 Y158.945048 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0002
G0 X169.440962 Y158.945048 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0003 note=intra-page lift
G0 X165.524394 Y165.479447 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0003 note=intra-page XY
G0 X165.524394 Y165.479447 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0003 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0003
G1 X164.87081 Y165.087704 Z2 E677.508609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X164.20366 Y164.772166 Z2 E677.763091 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X163.904101 Y164.630485 Z2 E677.931377 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X162.897232 Y164.270221 Z2 E678.702804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X162.800962 Y164.246107 Z2 E678.792077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X161.859899 Y164.010383 Z2 E679.822889 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X161.33577 Y163.932636 Z2 E680.507052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X160.802093 Y163.853472 Z2 E681.291632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X159.842767 Y163.806343 Z2 E682.908018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X159.734 Y163.801 Z2 E683.109034 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X158.665907 Y163.853472 Z2 E685.275095 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X158.347668 Y163.900678 Z2 E685.994975 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X157.608101 Y164.010383 Z2 E687.789814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X156.878307 Y164.193187 Z2 E689.767921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X156.570768 Y164.270221 Z2 E690.653191 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X155.563899 Y164.630485 Z2 E693.865227 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X155.461225 Y164.679046 Z2 E694.226858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X154.59719 Y165.087704 Z2 E697.425922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X154.130416 Y165.367477 Z2 E699.371785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X153.679951 Y165.637476 Z2 E701.335275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X152.896971 Y166.218173 Z2 E705.202703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X152.821016 Y166.274505 Z2 E705.593287 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X152.028657 Y166.992657 Z2 E710.199957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X151.802977 Y167.241658 Z2 E711.71961 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X151.310505 Y167.785016 Z2 E715.073307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X150.673476 Y168.643951 Z2 E719.963873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X150.123704 Y169.56119 Z2 E724.854439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X149.666485 Y170.527899 Z2 E729.745005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X149.306221 Y171.534768 Z2 E734.635571 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X149.046383 Y172.572101 Z2 E739.526137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X148.889472 Y173.629907 Z2 E744.416703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X148.837 Y174.698 Z2 E749.30727 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X148.889472 Y175.766093 Z2 E754.197836 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X149.046383 Y176.823899 Z2 E759.088402 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X149.306221 Y177.861232 Z2 E763.978968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X149.666485 Y178.868101 Z2 E768.869534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X150.123704 Y179.83481 Z2 E773.7601 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X150.673476 Y180.752049 Z2 E778.650666 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X151.310505 Y181.610984 Z2 E783.541232 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X152.028657 Y182.403343 Z2 E788.431798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X152.821016 Y183.121495 Z2 E793.322364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X153.679951 Y183.758524 Z2 E798.21293 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X154.59719 Y184.308296 Z2 E803.103496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X155.563899 Y184.765515 Z2 E807.994062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X156.570768 Y185.125779 Z2 E812.884628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X157.608101 Y185.385617 Z2 E817.775194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X158.665907 Y185.542528 Z2 E822.66576 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X159.734 Y185.595 Z2 E827.556326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X160.802093 Y185.542528 Z2 E832.446892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X161.859899 Y185.385617 Z2 E837.337458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X162.897232 Y185.125779 Z2 E842.228024 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X163.904101 Y184.765515 Z2 E847.11859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X164.87081 Y184.308296 Z2 E852.009156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X165.788049 Y183.758524 Z2 E856.899722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X166.646984 Y183.121495 Z2 E861.790288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X167.439343 Y182.403343 Z2 E866.680854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X168.157495 Y181.610984 Z2 E871.57142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X168.322816 Y181.388075 Z2 E872.84061 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X168.794524 Y180.752049 Z2.395929 E876.889432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2 matz1=2.395929 note=collision lift
G1 X169.344296 Y179.83481 Z2.930619 E882.357251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X169.801515 Y178.868101 Z3.46531 E887.82507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X170.161779 Y177.861232 Z4 E893.292889 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=3.46531 matz1=4 note=collision lift
G1 X170.421617 Y176.823899 Z4 E898.183455 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X170.578528 Y175.766093 Z3.46531 E903.651274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=3.46531 note=collision lift
G1 X170.631 Y174.698 Z2.930619 E909.119093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X170.578528 Y173.629907 Z2.395929 E914.586912 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X170.462338 Y172.846621 Z2 E918.635734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2.395929 matz1=2 note=collision lift
G1 X170.421617 Y172.572101 Z2 E919.904924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X170.161779 Y171.534768 Z2 E924.79549 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X169.801515 Y170.527899 Z2 E929.686056 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X169.344296 Y169.56119 Z2 E934.576622 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X169.007923 Y168.999985 Z2 E937.568874 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X168.794524 Y168.643951 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X168.157495 Y167.785016 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X167.439343 Y166.992657 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X166.646984 Y166.274505 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X165.788049 Y165.637476 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X165.524394 Y165.479447 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0003
G0 X165.524394 Y165.479447 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0004 note=intra-page lift
G0 X155.533631 Y151.75749 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0004 note=intra-page XY
G0 X155.533631 Y151.75749 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0004 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0004
G1 X156.674456 Y150.783572 Z2 E937.911869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X156.934 Y150.562 Z2 E938.085689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X157.686347 Y149.680718 Z2 E938.940855 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X158.12949 Y149.161631 Z2 E939.636132 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X158.568194 Y148.471834 Z2 E940.65583 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X158.608459 Y148.408524 Z2 E940.759628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X158.994922 Y147.617672 Z2 E942.105531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.171174 Y147.10223 Z2 E943.056796 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.278886 Y146.787228 Z2 E943.682684 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.450361 Y145.915346 Z2 E945.518735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.46525 Y145.637238 Z2 E946.143753 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.499355 Y145.000177 Z2 E947.664609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.4247 Y144.141389 Z2 E949.916699 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.415875 Y144.039875 Z2 E950.197882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.18993 Y143.032593 Z2 E953.225031 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X159.066549 Y142.688238 Z2 E954.375636 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X158.811529 Y141.976482 Z2 E956.883151 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X158.484904 Y141.308082 Z2 E959.520563 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X158.27068 Y140.869698 Z2 E961.341995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X157.740326 Y140.007714 Z2 E965.351481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X157.557391 Y139.710391 Z2 E966.806909 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X156.873966 Y138.78437 Z2 E971.868388 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X156.66167 Y138.496715 Z2 E973.503388 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X155.573525 Y137.226822 Z2 E981.151398 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X154.282966 Y135.898866 Z2 E989.619987 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X152.78 Y134.511 Z2 E998.975737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X151.566027 Y132.980941 Z2 E1007.908033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X149.578781 Y130.913906 Z2 E1021.021263 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X146.851145 Y128.48223 Z2 E1037.73282 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X143.416 Y125.85825 Z2 E1057.501559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X141.443388 Y124.528 Z2 E1068.382442 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X139.30623 Y123.214301 Z2 E1079.855104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X137.008637 Y121.938693 Z2 E1091.873416 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X134.554719 Y120.722719 Z2 E1104.398085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X131.948585 Y119.58792 Z2 E1117.397514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X129.194348 Y118.55584 Z2 E1130.84869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X126.296116 Y117.648019 Z2 E1144.738097 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X123.258 Y116.886 Z2 E1159.062594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X124.020019 Y119.924116 Z2 E1173.38709 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X124.92784 Y122.822348 Z2 E1187.276497 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X125.95992 Y125.576585 Z2 E1200.727673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X127.094719 Y128.182719 Z2 E1213.727102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X128.310693 Y130.636637 Z2 E1226.251771 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X129.586301 Y132.93423 Z2 E1238.270083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X130.9 Y135.071388 Z2 E1249.742745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X132.23025 Y137.044 Z2 E1260.623628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X134.85423 Y140.479145 Z2 E1280.392367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X137.285906 Y143.206781 Z2 E1297.103924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X139.352941 Y145.194027 Z2 E1310.217154 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X140.883 Y146.408 Z2 E1319.14945 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X142.270866 Y147.910966 Z2 E1328.5052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X143.598822 Y149.201525 Z2 E1336.973789 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X144.868715 Y150.28967 Z2 E1344.621799 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X146.082391 Y151.185391 Z2 E1351.520201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X147.241698 Y151.89868 Z2 E1357.745181 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X148.348482 Y152.439529 Z2 E1363.378829 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X149.404593 Y152.81793 Z2 E1368.509368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X150.411875 Y153.043875 Z2 E1373.23041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X150.82968 Y153.080195 Z2 E1375.148351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X151.372177 Y153.127355 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X152.287346 Y153.078361 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X153.159228 Y152.906886 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X153.989672 Y152.622922 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X154.780524 Y152.236459 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X155.533631 Y151.75749 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0004
G0 X155.533631 Y151.75749 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0005 note=intra-page lift
G0 X140.9912 Y150.325186 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0005 note=intra-page XY
G0 X140.9912 Y150.325186 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0005 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0005
G1 X141.012 Y150.114 Z2 E1375.155216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X140.885774 Y148.832409 Z2 E1375.491346 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X140.865584 Y148.627412 Z2 E1375.592018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X140.489952 Y147.38912 Z2 E1376.520331 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X140.431962 Y147.197952 Z2 E1376.709135 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X139.819038 Y146.051252 Z2 E1378.235307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X139.727798 Y145.880555 Z2 E1378.506566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X138.898996 Y144.870656 Z2 E1380.636273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X138.780154 Y144.725846 Z2 E1380.984312 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X137.765448 Y143.893099 Z2 E1383.723229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X137.625445 Y143.778202 Z2 E1384.142371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X136.462291 Y143.156483 Z2 E1387.496176 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X136.308048 Y143.074038 Z2 E1387.980744 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X135.040001 Y142.68938 Z2 E1391.955113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X134.878588 Y142.640416 Z2 E1392.499431 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X133.553675 Y142.509924 Z2 E1397.10004 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X133.392 Y142.494 Z2 E1397.698432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X132.060898 Y142.625102 Z2 E1402.930957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X131.905412 Y142.640416 Z2 E1403.577748 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X130.619512 Y143.03049 Z2 E1409.447865 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X130.475952 Y143.074038 Z2 E1410.133946 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X129.158555 Y143.778202 Z2 E1416.965409 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X128.003846 Y144.725846 Z2 E1423.796871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X127.056202 Y145.880555 Z2 E1430.628334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X126.352038 Y147.197952 Z2 E1437.459797 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X125.918416 Y148.627412 Z2 E1444.291259 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X125.772 Y150.114 Z2 E1451.122722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X125.918416 Y151.600588 Z2 E1457.954185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X126.352038 Y153.030048 Z2 E1464.785648 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X127.056202 Y154.347445 Z2 E1471.61711 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X128.003846 Y155.502154 Z2 E1478.448573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X129.158555 Y156.449798 Z2 E1485.280036 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X130.475952 Y157.153962 Z2 E1492.111498 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X131.905412 Y157.587584 Z2 E1498.942961 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X133.392 Y157.734 Z2 E1505.774424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X134.878588 Y157.587584 Z2 E1512.605886 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X136.308048 Y157.153962 Z2 E1519.437349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X137.625445 Y156.449798 Z2 E1526.268812 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X138.780154 Y155.502154 Z2 E1533.100275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X139.264143 Y154.912411 Z2 E1536.5893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X139.727798 Y154.347445 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
G1 X140.431962 Y153.030048 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
G1 X140.865584 Y151.600588 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
G1 X140.9912 Y150.325186 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0005
G0 X140.9912 Y150.325186 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0006 note=intra-page lift
G0 X139.466093 Y163.853472 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0006 note=intra-page XY
G0 X139.466093 Y163.853472 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0006 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0006
G1 X138.398 Y163.801 Z2 E1536.763629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X137.9679 Y163.822129 Z2 E1536.932295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X137.329907 Y163.853472 Z2 E1537.286617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X136.477991 Y163.979842 Z2 E1537.96128 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X136.272101 Y164.010383 Z2 E1538.158263 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X135.234768 Y164.270221 Z2 E1539.378568 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X135.025297 Y164.345171 Z2 E1539.676256 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X134.227899 Y164.630485 Z2 E1540.947531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X133.637507 Y164.909719 Z2 E1542.077222 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X133.26119 Y165.087704 Z2 E1542.865153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X132.343951 Y165.637476 Z2 E1545.131434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X132.332438 Y165.646014 Z2 E1545.164178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X131.485016 Y166.274505 Z2 E1547.746373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X131.155328 Y166.573317 Z2 E1548.937125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X130.692657 Y166.992657 Z2 E1550.70997 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X130.104659 Y167.641413 Z2 E1553.396062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X129.974505 Y167.785016 Z2 E1554.022226 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X129.337476 Y168.643951 Z2 E1557.683141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X129.215731 Y168.84707 Z2 E1558.540989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X128.787704 Y169.56119 Z2 E1561.692714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X128.502341 Y170.164539 Z2 E1564.371906 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X128.330485 Y170.527899 Z2 E1566.050945 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X127.970221 Y171.534768 Z2 E1570.757835 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X127.963256 Y171.562576 Z2 E1570.888814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X127.710383 Y172.572101 Z2 E1575.648276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X127.553472 Y173.629907 Z2 E1580.538842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X127.501 Y174.698 Z2 E1585.429408 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X127.553472 Y175.766093 Z2 E1590.319974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X127.710383 Y176.823899 Z2 E1595.21054 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X127.970221 Y177.861232 Z2 E1600.101106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X128.330485 Y178.868101 Z2 E1604.991672 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X128.787704 Y179.83481 Z2 E1609.882238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X129.337476 Y180.752049 Z2 E1614.772804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X129.974505 Y181.610984 Z2 E1619.66337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X130.692657 Y182.403343 Z2 E1624.553936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X131.485016 Y183.121495 Z2 E1629.444502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X132.343951 Y183.758524 Z2 E1634.335068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X133.26119 Y184.308296 Z2 E1639.225635 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X134.227899 Y184.765515 Z2 E1644.116201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X135.234768 Y185.125779 Z2 E1649.006767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X136.272101 Y185.385617 Z2 E1653.897333 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X137.329907 Y185.542528 Z2 E1658.787899 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X138.398 Y185.595 Z2 E1663.678465 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X139.466093 Y185.542528 Z2 E1668.569031 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X140.523899 Y185.385617 Z2 E1673.459597 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X141.561232 Y185.125779 Z2 E1678.350163 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X142.568101 Y184.765515 Z2 E1683.240729 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X143.53481 Y184.308296 Z2 E1688.131295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X144.452049 Y183.758524 Z2 E1693.021861 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X145.310984 Y183.121495 Z2 E1697.912427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X146.103343 Y182.403343 Z2 E1702.802993 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X146.821495 Y181.610984 Z2 E1707.693559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X146.986816 Y181.388075 Z2 E1708.962749 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X147.458524 Y180.752049 Z2.395929 E1713.01157 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=2 matz1=2.395929 note=collision lift
G1 X148.008296 Y179.83481 Z2.930619 E1718.47939 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X148.465515 Y178.868101 Z3.46531 E1723.947209 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X148.825779 Y177.861232 Z4 E1729.415028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=3.46531 matz1=4 note=collision lift
G1 X149.085617 Y176.823899 Z4 E1734.305594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=4 matz1=4 note=collision lift
G1 X149.242528 Y175.766093 Z3.46531 E1739.773413 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=4 matz1=3.46531 note=collision lift
G1 X149.295 Y174.698 Z2.930619 E1745.241232 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X149.242528 Y173.629907 Z2.395929 E1750.709051 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X149.126338 Y172.846621 Z2 E1754.757872 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=2.395929 matz1=2 note=collision lift
G1 X149.085617 Y172.572101 Z2 E1756.027062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X148.825779 Y171.534768 Z2 E1760.917628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X148.465515 Y170.527899 Z2 E1765.808194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X148.008296 Y169.56119 Z2 E1770.69876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X147.458524 Y168.643951 Z2 E1775.589326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X146.821495 Y167.785016 Z2 E1780.479892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X146.103343 Y166.992657 Z2 E1785.370458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X145.310984 Y166.274505 Z2 E1790.261025 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X144.452049 Y165.637476 Z2 E1795.151591 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X144.154499 Y165.459131 Z2 E1796.738078 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X143.53481 Y165.087704 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X142.568101 Y164.630485 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X141.561232 Y164.270221 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X140.523899 Y164.010383 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X139.466093 Y163.853472 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0006
G0 X139.466093 Y163.853472 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0007 note=intra-page lift
G0 X126.804982 Y169.841731 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0007 note=intra-page XY
G0 X126.804982 Y169.841731 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0007 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0007
G1 X126.672296 Y169.56119 Z2 E1796.752759 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X126.122524 Y168.643951 Z2 E1797.02827 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X126.050873 Y168.54734 Z2 E1797.081073 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X125.485495 Y167.785016 Z2 E1797.65244 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X125.115532 Y167.376826 Z2 E1798.110058 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X124.767343 Y166.992657 Z2 E1798.625268 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X124.040084 Y166.333509 Z2 E1799.825034 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X123.974984 Y166.274505 Z2 E1799.946754 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X123.116049 Y165.637476 Z2 E1801.616899 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X122.822055 Y165.461263 Z2 E1802.226 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X122.19881 Y165.087704 Z2 E1803.635703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X121.499685 Y164.757043 Z2 E1805.312956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X121.232101 Y164.630485 Z2 E1806.003165 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X120.225232 Y164.270221 Z2 E1808.719286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X120.094651 Y164.237512 Z2 E1809.085903 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X119.187899 Y164.010383 Z2 E1811.784065 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X118.628782 Y163.927446 Z2 E1813.54484 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X118.130093 Y163.853472 Z2 E1815.197502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X117.135439 Y163.804608 Z2 E1818.689767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X117.062 Y163.801 Z2 E1818.959598 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X115.993907 Y163.853472 Z2 E1823.070353 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X115.64068 Y163.905868 Z2 E1824.520684 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X114.936101 Y164.010383 Z2 E1827.529766 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X114.171996 Y164.201781 Z2 E1831.037592 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X113.898768 Y164.270221 Z2 E1832.325744 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X112.891899 Y164.630485 Z2 E1837.21631 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X111.92519 Y165.087704 Z2 E1842.106876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X111.007951 Y165.637476 Z2 E1846.997442 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X110.149016 Y166.274505 Z2 E1851.888008 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X109.356657 Y166.992657 Z2 E1856.778574 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X108.638505 Y167.785016 Z2 E1861.66914 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X108.001476 Y168.643951 Z2 E1866.559706 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X107.451704 Y169.56119 Z2 E1871.450272 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.994485 Y170.527899 Z2 E1876.340838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.634221 Y171.534768 Z2 E1881.231404 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.374383 Y172.572101 Z2 E1886.12197 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.217472 Y173.629907 Z2 E1891.012536 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.165 Y174.698 Z2 E1895.903102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.217472 Y175.766093 Z2 E1900.793668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.374383 Y176.823899 Z2 E1905.684234 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.634221 Y177.861232 Z2 E1910.5748 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X106.994485 Y178.868101 Z2 E1915.465366 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X107.451704 Y179.83481 Z2 E1920.355932 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X108.001476 Y180.752049 Z2 E1925.246498 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X108.638505 Y181.610984 Z2 E1930.137064 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X109.356657 Y182.403343 Z2 E1935.02763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X110.149016 Y183.121495 Z2 E1939.918196 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X111.007951 Y183.758524 Z2 E1944.808762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X111.92519 Y184.308296 Z2 E1949.699328 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X112.891899 Y184.765515 Z2 E1954.589894 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X113.898768 Y185.125779 Z2 E1959.480461 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X114.936101 Y185.385617 Z2 E1964.371027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X115.993907 Y185.542528 Z2 E1969.261593 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X117.062 Y185.595 Z2 E1974.152159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X118.130093 Y185.542528 Z2 E1979.042725 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X119.187899 Y185.385617 Z2 E1983.933291 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X120.225232 Y185.125779 Z2 E1988.823857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X121.232101 Y184.765515 Z2 E1993.714423 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X122.19881 Y184.308296 Z2 E1998.604989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X123.116049 Y183.758524 Z2 E2003.495555 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X123.974984 Y183.121495 Z2 E2008.386121 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X124.767343 Y182.403343 Z2 E2013.276687 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X125.485495 Y181.610984 Z2 E2018.167253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X125.650816 Y181.388075 Z2 E2019.436443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X126.122524 Y180.752049 Z2.395929 E2023.485264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2 matz1=2.395929 note=collision lift
G1 X126.672296 Y179.83481 Z2.930619 E2028.953083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X127.129515 Y178.868101 Z3.46531 E2034.420902 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X127.489779 Y177.861232 Z4 E2039.888722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.46531 matz1=4 note=collision lift
G1 X127.749617 Y176.823899 Z4 E2044.779288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=4 matz1=4 note=collision lift
G1 X127.906528 Y175.766093 Z3.46531 E2050.247107 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=4 matz1=3.46531 note=collision lift
G1 X127.959 Y174.698 Z2.930619 E2055.714926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X127.947754 Y174.469073 Z2.816018 E2056.886856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.930619 matz1=2.816018 note=collision lift
G1 X127.906528 Y173.629907 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.816018 matz1=2.395929 note=collision lift
G1 X127.790338 Y172.846621 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.395929 matz1=2 note=collision lift
G1 X127.749617 Y172.572101 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
G1 X127.489779 Y171.534768 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
G1 X127.129515 Y170.527899 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
G1 X126.804982 Y169.841731 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0007
G0 X126.804982 Y169.841731 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0008 note=intra-page lift
G0 X122.089446 Y162.273704 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0008 note=intra-page XY
G0 X122.089446 Y162.273704 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0008 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0008
G1 X122.126627 Y162.250537 Z2 E2056.887148 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X122.808376 Y161.682097 Z2 E2057.019114 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X123.189913 Y161.260577 Z2 E2057.229851 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X123.428375 Y160.997125 Z2 E2057.411609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X123.980862 Y160.187852 Z2 E2058.112264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X124.055615 Y160.041011 Z2 E2058.258836 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X124.460076 Y159.24651 Z2 E2059.195439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X124.671289 Y158.675871 Z2 E2059.973812 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X124.860256 Y158.165331 Z2 E2060.765881 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.097827 Y157.239722 Z2 E2062.374778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.175641 Y156.936547 Z2 E2062.962289 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.36595 Y155.764904 Z2 E2065.461734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.400469 Y155.55239 Z2 E2065.961111 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.506803 Y154.272097 Z2 E2069.234681 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.528979 Y154.005092 Z2 E2069.980799 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.547929 Y152.773162 Z2 E2073.693618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.555409 Y152.286885 Z2 E2075.286573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.511946 Y151.274152 Z2 E2078.838545 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.474 Y150.39 Z2 E2082.195682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.549853 Y149.779661 Z2 E2084.669462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.697758 Y148.58957 Z2 E2089.824733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.70415 Y148.288885 Z2 E2091.18637 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X125.754313 Y145.929313 Z2 E2101.979767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X125.545086 Y142.543898 Z2 E2117.491714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X124.9715 Y138.568 Z2 E2135.862807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X124.517267 Y136.400704 Z2 E2145.989783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X123.934977 Y134.136289 Z2 E2156.682469 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X123.212308 Y131.791589 Z2 E2167.903177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X122.336938 Y129.383438 Z2 E2179.621338 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X121.296544 Y126.928669 Z2 E2191.814317 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X120.078805 Y124.444117 Z2 E2204.468218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X118.671397 Y121.946616 Z2 E2217.578676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X117.062 Y119.453 Z2 E2231.151566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X115.452603 Y121.946616 Z2 E2244.724455 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X114.045195 Y124.444117 Z2 E2257.834913 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X112.827456 Y126.928669 Z2 E2270.488815 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X111.787063 Y129.383438 Z2 E2282.681793 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X110.911692 Y131.791589 Z2 E2294.399955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X110.189023 Y134.136289 Z2 E2305.620662 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X109.606733 Y136.400704 Z2 E2316.313349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X109.1525 Y138.568 Z2 E2326.440324 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X108.578914 Y142.543898 Z2 E2344.811418 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X108.369688 Y145.929313 Z2 E2360.323365 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X108.426242 Y148.58957 Z2 E2372.492187 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X108.65 Y150.39 Z2 E2380.78938 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X108.568591 Y152.286885 Z2 E2389.472328 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X108.595021 Y154.005092 Z2 E2397.331081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X108.723531 Y155.55239 Z2 E2404.431655 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X108.948359 Y156.936547 Z2 E2410.844738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X109.263744 Y158.165331 Z2 E2416.646443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X109.663924 Y159.24651 Z2 E2421.918793 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X110.143138 Y160.187852 Z2 E2426.749539 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X110.695625 Y160.997125 Z2 E2431.230794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X111.315624 Y161.682097 Z2 E2435.456023 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X111.997373 Y162.250537 Z2 E2439.515442 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X112.735112 Y162.710212 Z2 E2443.49066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X113.523078 Y163.068891 Z2 E2447.450016 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X114.355511 Y163.334341 Z2 E2451.445831 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X115.22665 Y163.51433 Z2 E2455.513931 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X117.062 Y163.649 Z2 E2463.930042 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X117.355946 Y163.627432 Z2 E2465.277952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X118.89735 Y163.51433 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X119.768489 Y163.334341 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X120.600922 Y163.068891 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X121.388888 Y162.710212 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X122.089446 Y162.273704 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0008
G0 X122.089446 Y162.273704 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0009 note=intra-page lift
G0 X107.11061 Y154.26735 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0009 note=intra-page XY
G0 X107.11061 Y154.26735 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0009 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0009
G1 X107.771962 Y153.030048 Z2 E2465.578005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X107.800131 Y152.937189 Z2 E2465.620947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X108.205584 Y151.600588 Z2 E2466.557114 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X108.215705 Y151.497829 Z2 E2466.649932 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X108.352 Y150.114 Z2 E2468.216537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X108.34127 Y150.005052 Z2 E2468.364908 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X108.205584 Y148.627412 Z2 E2470.556275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X108.172 Y148.516699 Z2 E2470.765874 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X107.771962 Y147.197952 Z2 E2473.576326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X107.714493 Y147.090435 Z2 E2473.85283 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X107.067798 Y145.880555 Z2 E2477.276692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X106.986513 Y145.781508 Z2 E2477.625777 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X106.120154 Y144.725846 Z2 E2481.657371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X106.016299 Y144.640615 Z2 E2482.084714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X104.965445 Y143.778202 Z2 E2486.718365 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X104.841474 Y143.711938 Z2 E2487.229641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X103.648048 Y143.074038 Z2 E2492.459673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X103.50758 Y143.031428 Z2 E2493.060558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X102.218588 Y142.640416 Z2 E2498.881294 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X102.066318 Y142.625419 Z2 E2499.577466 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X100.732 Y142.494 Z2 E2505.709188 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X99.245412 Y142.640416 Z2 E2512.540651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X97.815952 Y143.074038 Z2 E2519.372114 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X96.498555 Y143.778202 Z2 E2526.203576 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X95.343846 Y144.725846 Z2 E2533.035039 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X94.396202 Y145.880555 Z2 E2539.866502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X93.692038 Y147.197952 Z2 E2546.697964 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X93.258416 Y148.627412 Z2 E2553.529427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X93.112 Y150.114 Z2 E2560.36089 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X93.258416 Y151.600588 Z2 E2567.192352 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X93.692038 Y153.030048 Z2 E2574.023815 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X94.396202 Y154.347445 Z2 E2580.855278 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X95.343846 Y155.502154 Z2 E2587.686741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X96.498555 Y156.449798 Z2 E2594.518203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X97.815952 Y157.153962 Z2 E2601.349666 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X99.245412 Y157.587584 Z2 E2608.181129 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X100.732 Y157.734 Z2 E2615.012591 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X102.218588 Y157.587584 Z2 E2621.844054 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X103.238633 Y157.278157 Z2 E2626.718901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X103.648048 Y157.153962 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X104.965445 Y156.449798 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X106.120154 Y155.502154 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X107.067798 Y154.347445 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X107.11061 Y154.26735 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0009
G0 X107.11061 Y154.26735 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0010 note=intra-page lift
G0 X100.86281 Y165.087704 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0010 note=intra-page XY
G0 X100.86281 Y165.087704 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0010 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0010
G1 X99.896101 Y164.630485 Z2 E2626.89323 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X99.490654 Y164.485414 Z2 E2627.061896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X98.889232 Y164.270221 Z2 E2627.416218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X98.053804 Y164.060957 Z2 E2628.090882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X97.851899 Y164.010383 Z2 E2628.287864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X96.794093 Y163.853472 Z2 E2629.508169 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X96.571884 Y163.842556 Z2 E2629.805857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X95.726 Y163.801 Z2 E2631.077133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X95.073691 Y163.833046 Z2 E2632.206823 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X94.657907 Y163.853472 Z2 E2632.994755 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X93.600101 Y164.010383 Z2 E2635.261035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X93.586197 Y164.013866 Z2 E2635.29378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X92.562768 Y164.270221 Z2 E2637.875974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X92.143825 Y164.420121 Z2 E2639.066726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X91.555899 Y164.630485 Z2 E2640.839571 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X90.764391 Y165.00484 Z2 E2643.525663 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X90.58919 Y165.087704 Z2 E2644.151827 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X89.671951 Y165.637476 Z2 E2647.812742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X89.481743 Y165.778543 Z2 E2648.67059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X88.813016 Y166.274505 Z2 E2651.822315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X88.318484 Y166.722723 Z2 E2654.501508 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X88.020657 Y166.992657 Z2 E2656.180546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X87.302505 Y167.785016 Z2 E2660.887437 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X87.285428 Y167.808042 Z2 E2661.018415 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X86.665476 Y168.643951 Z2 E2665.777877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X86.115704 Y169.56119 Z2 E2670.668443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X85.658485 Y170.527899 Z2 E2675.559009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X85.298221 Y171.534768 Z2 E2680.449575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X85.038383 Y172.572101 Z2 E2685.340141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X84.881472 Y173.629907 Z2 E2690.230707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X84.829 Y174.698 Z2 E2695.121273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X84.881472 Y175.766093 Z2 E2700.011839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X85.038383 Y176.823899 Z2 E2704.902406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X85.298221 Y177.861232 Z2 E2709.792972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X85.658485 Y178.868101 Z2 E2714.683538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X86.115704 Y179.83481 Z2 E2719.574104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X86.665476 Y180.752049 Z2 E2724.46467 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X87.302505 Y181.610984 Z2 E2729.355236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X88.020657 Y182.403343 Z2 E2734.245802 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X88.813016 Y183.121495 Z2 E2739.136368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X89.671951 Y183.758524 Z2 E2744.026934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X90.58919 Y184.308296 Z2 E2748.9175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X91.555899 Y184.765515 Z2 E2753.808066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X92.562768 Y185.125779 Z2 E2758.698632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X93.600101 Y185.385617 Z2 E2763.589198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X94.657907 Y185.542528 Z2 E2768.479764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X95.726 Y185.595 Z2 E2773.37033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X96.794093 Y185.542528 Z2 E2778.260896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X97.851899 Y185.385617 Z2 E2783.151462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X98.889232 Y185.125779 Z2 E2788.042028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X99.896101 Y184.765515 Z2 E2792.932594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X100.86281 Y184.308296 Z2 E2797.82316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X101.780049 Y183.758524 Z2 E2802.713726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X102.638984 Y183.121495 Z2 E2807.604292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X103.431343 Y182.403343 Z2 E2812.494858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X104.149495 Y181.610984 Z2 E2817.385424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X104.314816 Y181.388075 Z2 E2818.654614 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X104.786524 Y180.752049 Z2.395929 E2822.703436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2 matz1=2.395929 note=collision lift
G1 X105.336296 Y179.83481 Z2.930619 E2828.171255 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X105.793515 Y178.868101 Z3.46531 E2833.639074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X106.153779 Y177.861232 Z4 E2839.106893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=3.46531 matz1=4 note=collision lift
G1 X106.413617 Y176.823899 Z4 E2843.997459 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X106.570528 Y175.766093 Z3.46531 E2849.465278 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=3.46531 note=collision lift
G1 X106.623 Y174.698 Z2.930619 E2854.933097 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X106.570528 Y173.629907 Z2.395929 E2860.400916 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X106.454338 Y172.846621 Z2 E2864.449738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2.395929 matz1=2 note=collision lift
G1 X106.413617 Y172.572101 Z2 E2865.718928 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X106.153779 Y171.534768 Z2 E2870.609494 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X105.793515 Y170.527899 Z2 E2875.50006 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X105.336296 Y169.56119 Z2 E2880.390626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X104.786524 Y168.643951 Z2 E2885.281192 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X104.579874 Y168.365315 Z2 E2886.867679 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X104.149495 Y167.785016 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X103.431343 Y166.992657 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X102.638984 Y166.274505 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X101.780049 Y165.637476 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X100.86281 Y165.087704 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0010
G0 X100.86281 Y165.087704 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0011 note=intra-page lift
G0 X84.593819 Y170.908842 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0011 note=intra-page XY
G0 X84.593819 Y170.908842 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0011 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0011
G1 X84.457515 Y170.527899 Z2 E2886.892633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X84.000296 Y169.56119 Z2 E2887.198876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X83.986917 Y169.538868 Z2 E2887.210674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X83.450524 Y168.643951 Z2 E2887.853776 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X83.178502 Y168.277171 Z2 E2888.23966 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X82.813495 Y167.785016 Z2 E2888.857336 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X82.217646 Y167.127598 Z2 E2889.954635 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X82.095343 Y166.992657 Z2 E2890.209554 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X81.302984 Y166.274505 Z2 E2891.91043 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X81.103386 Y166.126473 Z2 E2892.355601 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X80.444049 Y165.637476 Z2 E2893.959965 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X79.861548 Y165.288338 Z2 E2895.442558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X79.52681 Y165.087704 Z2 E2896.358159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X78.560101 Y164.630485 Z2 E2899.105011 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X78.522102 Y164.616888 Z2 E2899.215504 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X77.553232 Y164.270221 Z2 E2902.200521 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X77.096369 Y164.155783 Z2 E2903.674441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X76.515899 Y164.010383 Z2 E2905.64469 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X75.624061 Y163.878091 Z2 E2908.819368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X75.458093 Y163.853472 Z2 E2909.437518 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X74.39 Y163.801 Z2 E2913.579004 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X74.127482 Y163.813897 Z2 E2914.650286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X73.321907 Y163.853472 Z2 E2918.069148 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X72.635959 Y163.955223 Z2 E2921.167193 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X72.264101 Y164.010383 Z2 E2922.886408 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X71.226768 Y164.270221 Z2 E2927.776974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X70.219899 Y164.630485 Z2 E2932.66754 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X69.25319 Y165.087704 Z2 E2937.558106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X68.335951 Y165.637476 Z2 E2942.448672 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X67.477016 Y166.274505 Z2 E2947.339238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X66.684657 Y166.992657 Z2 E2952.229804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X65.966505 Y167.785016 Z2 E2957.12037 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X65.329476 Y168.643951 Z2 E2962.010936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X64.779704 Y169.56119 Z2 E2966.901502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X64.322485 Y170.527899 Z2 E2971.792069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X63.962221 Y171.534768 Z2 E2976.682635 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X63.702383 Y172.572101 Z2 E2981.573201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X63.545472 Y173.629907 Z2 E2986.463767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X63.493 Y174.698 Z2 E2991.354333 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X63.545472 Y175.766093 Z2 E2996.244899 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X63.702383 Y176.823899 Z2 E3001.135465 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X63.962221 Y177.861232 Z2 E3006.026031 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X64.322485 Y178.868101 Z2 E3010.916597 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X64.779704 Y179.83481 Z2 E3015.807163 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X65.329476 Y180.752049 Z2 E3020.697729 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X65.966505 Y181.610984 Z2 E3025.588295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X66.684657 Y182.403343 Z2 E3030.478861 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X67.477016 Y183.121495 Z2 E3035.369427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X68.335951 Y183.758524 Z2 E3040.259993 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X69.25319 Y184.308296 Z2 E3045.150559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X70.219899 Y184.765515 Z2 E3050.041125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X71.226768 Y185.125779 Z2 E3054.931691 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X72.264101 Y185.385617 Z2 E3059.822257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X73.321907 Y185.542528 Z2 E3064.712823 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X74.39 Y185.595 Z2 E3069.603389 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X75.458093 Y185.542528 Z2 E3074.493955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X76.515899 Y185.385617 Z2 E3079.384521 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X77.553232 Y185.125779 Z2 E3084.275087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X78.560101 Y184.765515 Z2 E3089.165653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X79.52681 Y184.308296 Z2 E3094.056219 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X80.444049 Y183.758524 Z2 E3098.946785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X81.302984 Y183.121495 Z2 E3103.837351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X82.095343 Y182.403343 Z2 E3108.727917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X82.813495 Y181.610984 Z2 E3113.618483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X82.978816 Y181.388075 Z2 E3114.887673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X83.450524 Y180.752049 Z2.395929 E3118.936495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2 matz1=2.395929 note=collision lift
G1 X84.000296 Y179.83481 Z2.930619 E3124.404314 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X84.457515 Y178.868101 Z3.46531 E3129.872133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X84.817779 Y177.861232 Z4 E3135.339952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=3.46531 matz1=4 note=collision lift
G1 X85.077617 Y176.823899 Z4 E3140.230518 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=4 matz1=4 note=collision lift
G1 X85.234528 Y175.766093 Z3.46531 E3145.698337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=4 matz1=3.46531 note=collision lift
G1 X85.247177 Y175.508609 Z3.336412 E3147.016457 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=3.46531 matz1=3.336412 note=collision lift
G1 X85.287 Y174.698 Z2.930619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=3.336412 matz1=2.930619 note=collision lift
G1 X85.234528 Y173.629907 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X85.118338 Y172.846621 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2.395929 matz1=2 note=collision lift
G1 X85.077617 Y172.572101 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=end-early tail
G1 X84.817779 Y171.534768 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=end-early tail
G1 X84.593819 Y170.908842 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0011
G0 X84.593819 Y170.908842 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0012 note=intra-page lift
G0 X76.92773 Y161.567686 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0012 note=intra-page XY
G0 X76.92773 Y161.567686 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0012 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0012
G1 X77.111154 Y161.417154 Z2 E3147.02504 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X77.912212 Y160.441062 Z2 E3147.359452 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X78.058798 Y160.262445 Z2 E3147.473264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X78.65697 Y159.143345 Z2 E3148.388438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X78.762962 Y158.945048 Z2 E3148.601802 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X79.133119 Y157.724803 Z2 E3150.103413 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X79.196584 Y157.515588 Z2 E3150.410654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X79.32218 Y156.240387 Z2 E3152.504379 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X79.343 Y156.029 Z2 E3152.89982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X79.216794 Y154.74761 Z2 E3155.591336 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X79.196584 Y154.542412 Z2 E3156.0693 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X78.821011 Y153.304314 Z2 E3159.364282 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X78.762962 Y153.112952 Z2 E3159.919094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X78.150133 Y151.96643 Z2 E3163.823219 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X78.058798 Y151.795555 Z2 E3164.449202 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X77.230124 Y150.785813 Z2 E3168.968146 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X77.111154 Y150.640846 Z2 E3169.659624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X76.096604 Y149.808227 Z2 E3174.799064 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X75.956445 Y149.693202 Z2 E3175.550361 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X74.79347 Y149.071578 Z2 E3181.315971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X74.639048 Y148.989038 Z2 E3182.116737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X73.209588 Y148.555416 Z2 E3188.9482 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X71.723 Y148.409 Z2 E3195.779663 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X70.236412 Y148.555416 Z2 E3202.611125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X68.806952 Y148.989038 Z2 E3209.442588 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X67.489555 Y149.693202 Z2 E3216.274051 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X66.334846 Y150.640846 Z2 E3223.105513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X65.387202 Y151.795555 Z2 E3229.936976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X64.683038 Y153.112952 Z2 E3236.768439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X64.249416 Y154.542412 Z2 E3243.599901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X64.103 Y156.029 Z2 E3250.431364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X64.249416 Y157.515588 Z2 E3257.262827 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X64.683038 Y158.945048 Z2 E3264.09429 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X65.387202 Y160.262445 Z2 E3270.925752 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X66.334846 Y161.417154 Z2 E3277.757215 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X67.489555 Y162.364798 Z2 E3284.588678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X68.806952 Y163.068962 Z2 E3291.42014 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X70.236412 Y163.502584 Z2 E3298.251603 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X71.723 Y163.649 Z2 E3305.083066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X72.457287 Y163.576679 Z2 E3308.457406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X73.209588 Y163.502584 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
G1 X74.639048 Y163.068962 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
G1 X75.956445 Y162.364798 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
G1 X76.92773 Y161.567686 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0012
G0 X76.92773 Y161.567686 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0013 note=intra-page lift
G0 X80.134328 Y152.622922 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0013 note=intra-page XY
G0 X80.134328 Y152.622922 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0013 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0013
G1 X80.964772 Y152.906886 Z2 E3308.574828 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X81.575422 Y153.026984 Z2 E3308.800401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X81.836654 Y153.078361 Z2 E3308.932964 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X82.751823 Y153.127355 Z2 E3309.554528 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X83.067915 Y153.099877 Z2 E3309.829387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X83.712125 Y153.043875 Z2 E3310.48458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X84.544795 Y152.857098 Z2 E3311.544362 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X84.719407 Y152.81793 Z2 E3311.794762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X85.775518 Y152.439529 Z2 E3313.586989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X85.954486 Y152.352073 Z2 E3313.945328 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X86.882302 Y151.89868 Z2 E3315.996966 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X87.280328 Y151.653786 Z2 E3317.032285 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X88.041609 Y151.185391 Z2 E3319.197955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X88.529329 Y150.825442 Z2 E3320.805231 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X89.255285 Y150.28967 Z2 E3323.405082 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X89.709186 Y149.900731 Z2 E3325.264168 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X90.525178 Y149.201525 Z2 E3328.880251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X90.830257 Y148.905037 Z2 E3330.409095 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X91.853134 Y147.910966 Z2 E3335.93767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X91.903104 Y147.856852 Z2 E3336.240013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X92.920727 Y146.754834 Z2 E3342.75692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X93.241 Y146.408 Z2 E3344.915913 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X94.771059 Y145.194027 Z2 E3353.848208 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X96.838094 Y143.206781 Z2 E3366.961438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X99.26977 Y140.479145 Z2 E3383.672996 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X101.89375 Y137.044 Z2 E3403.441735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X103.224 Y135.071388 Z2 E3414.322617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X104.537699 Y132.93423 Z2 E3425.795279 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X105.813307 Y130.636637 Z2 E3437.813591 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X107.029281 Y128.182719 Z2 E3450.338261 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X108.16408 Y125.576585 Z2 E3463.33769 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X109.19616 Y122.822348 Z2 E3476.788866 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X110.103981 Y119.924116 Z2 E3490.678273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X110.866 Y116.886 Z2 E3505.002769 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X107.827884 Y117.648019 Z2 E3519.327265 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X104.929652 Y118.55584 Z2 E3533.216672 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X102.175415 Y119.58792 Z2 E3546.667848 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X99.569281 Y120.722719 Z2 E3559.667277 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X97.115363 Y121.938693 Z2 E3572.191947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X94.81777 Y123.214301 Z2 E3584.210259 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X92.680612 Y124.528 Z2 E3595.682921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X90.708 Y125.85825 Z2 E3606.563803 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X87.272855 Y128.48223 Z2 E3626.332542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X84.545219 Y130.913906 Z2 E3643.0441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X82.557973 Y132.980941 Z2 E3656.15733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X81.344 Y134.511 Z2 E3665.089625 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X79.841034 Y135.898866 Z2 E3674.445375 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X78.550475 Y137.226822 Z2 E3682.913965 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X77.46233 Y138.496715 Z2 E3690.561975 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X76.566609 Y139.710391 Z2 E3697.460376 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X75.85332 Y140.869698 Z2 E3703.685356 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X75.312471 Y141.976482 Z2 E3709.319005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X74.93407 Y143.032593 Z2 E3714.449543 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X74.708125 Y144.039875 Z2 E3719.170585 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X74.624645 Y145.000177 Z2 E3723.578867 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X74.673639 Y145.915346 Z2 E3727.770173 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X74.845114 Y146.787228 Z2 E3731.833909 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X75.129078 Y147.617672 Z2 E3735.847646 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X75.515541 Y148.408524 Z2 E3739.873162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X75.99451 Y149.161631 Z2 E3743.954869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X76.290099 Y149.507877 Z2 E3746.036883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X77.19 Y150.562 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
G1 X78.590369 Y151.75749 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
G1 X79.343476 Y152.236459 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
G1 X80.134328 Y152.622922 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0013
G0 X80.134328 Y152.622922 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0014 note=intra-page lift
G0 X63.951 Y153.362 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0014 note=intra-page XY
G0 X63.951 Y153.362 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0014 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0014
G1 X63.898528 Y152.293907 Z2 E3746.211212 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X63.835343 Y151.867949 Z2 E3746.379878 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X63.741617 Y151.236101 Z2 E3746.7342 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X63.532353 Y150.400673 Z2 E3747.408863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X63.481779 Y150.198768 Z2 E3747.605846 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X63.121515 Y149.191899 Z2 E3748.826151 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X63.026394 Y148.990782 Z2 E3749.123839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X62.664296 Y148.22519 Z2 E3750.395114 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X62.328538 Y147.665011 Z2 E3751.524805 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X62.114524 Y147.307951 Z2 E3752.312736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X61.477495 Y146.449016 Z2 E3754.579017 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X61.467869 Y146.438396 Z2 E3754.611761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X60.759343 Y145.656657 Z2 E3757.193956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X60.429654 Y145.357845 Z2 E3758.384708 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X59.966984 Y144.938505 Z2 E3760.157553 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X59.263718 Y144.416927 Z2 E3762.843645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X59.108049 Y144.301476 Z2 E3763.469809 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X58.19081 Y143.751704 Z2 E3767.130724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X57.976736 Y143.650455 Z2 E3767.988572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X57.224101 Y143.294485 Z2 E3771.140297 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X56.595687 Y143.069635 Z2 E3773.819489 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X56.217232 Y142.934221 Z2 E3775.498528 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X55.179899 Y142.674383 Z2 E3780.205418 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X55.151542 Y142.670176 Z2 E3780.336397 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X54.122093 Y142.517472 Z2 E3785.095859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X53.054 Y142.465 Z2 E3789.986425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X51.985907 Y142.517472 Z2 E3794.876991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X50.928101 Y142.674383 Z2 E3799.767557 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X49.890768 Y142.934221 Z2 E3804.658123 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X48.883899 Y143.294485 Z2 E3809.548689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X47.91719 Y143.751704 Z2 E3814.439255 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X46.999951 Y144.301476 Z2 E3819.329821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X46.141016 Y144.938505 Z2 E3824.220387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X45.348657 Y145.656657 Z2 E3829.110953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X44.630505 Y146.449016 Z2 E3834.001519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X43.993476 Y147.307951 Z2 E3838.892085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X43.443704 Y148.22519 Z2 E3843.782651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.986485 Y149.191899 Z2 E3848.673217 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.626221 Y150.198768 Z2 E3853.563784 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.366383 Y151.236101 Z2 E3858.45435 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.209472 Y152.293907 Z2 E3863.344916 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.157 Y153.362 Z2 E3868.235482 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.209472 Y154.430093 Z2 E3873.126048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.366383 Y155.487899 Z2 E3878.016614 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.626221 Y156.525232 Z2 E3882.90718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X42.986485 Y157.532101 Z2 E3887.797746 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X43.443704 Y158.49881 Z2 E3892.688312 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X43.993476 Y159.416049 Z2 E3897.578878 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X44.630505 Y160.274984 Z2 E3902.469444 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X45.348657 Y161.067343 Z2 E3907.36001 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X46.141016 Y161.785495 Z2 E3912.250576 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X46.999951 Y162.422524 Z2 E3917.141142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X47.91719 Y162.972296 Z2 E3922.031708 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X48.883899 Y163.429515 Z2 E3926.922274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X49.890768 Y163.789779 Z2 E3931.81284 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X50.928101 Y164.049617 Z2 E3936.703406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X51.985907 Y164.206528 Z2 E3941.593972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X53.054 Y164.259 Z2 E3946.484538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X54.122093 Y164.206528 Z2 E3951.375104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X55.179899 Y164.049617 Z2 E3956.26567 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X56.217232 Y163.789779 Z2 E3961.156236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X57.224101 Y163.429515 Z2 E3966.046802 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X58.19081 Y162.972296 Z2 E3970.937368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X59.108049 Y162.422524 Z2 E3975.827934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X59.966984 Y161.785495 Z2 E3980.7185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X60.759343 Y161.067343 Z2 E3985.609066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X61.477495 Y160.274984 Z2 E3990.499632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X62.114524 Y159.416049 Z2 E3995.390198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X62.664296 Y158.49881 Z2 E4000.280764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X62.812617 Y158.185212 Z2 E4001.867252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X63.121515 Y157.532101 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X63.481779 Y156.525232 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X63.741617 Y155.487899 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X63.898528 Y154.430093 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X63.951 Y153.362 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0014
G0 X63.951 Y153.362 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0015 note=intra-page lift
G0 X58.19081 Y165.087704 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0015 note=intra-page XY
G0 X58.19081 Y165.087704 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0015 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0015
G1 X57.224101 Y164.630485 Z3 E4002.194023 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2 matz1=3 note=collision lift
G1 X57.19941 Y164.62165 Z3.024523 E4002.210247 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3 matz1=3.024523 note=collision lift
G1 X56.217232 Y164.270221 Z4 E4003.174338 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.024523 matz1=4 note=collision lift
G1 X56.147575 Y164.252773 Z4 E4003.239232 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=4 note=collision lift
G1 X55.179899 Y164.010383 Z4 E4004.303368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=4 note=collision lift
G1 X54.735378 Y163.944444 Z3.775307 E4004.954208 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=3.775307 note=collision lift
G1 X54.122093 Y163.853472 Z3.46531 E4005.978479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.775307 matz1=3.46531 note=collision lift
G1 X53.401317 Y163.818063 Z3.104487 E4007.355174 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.46531 matz1=3.104487 note=collision lift
G1 X53.054 Y163.801 Z2.930619 E4008.089414 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.104487 matz1=2.930619 note=collision lift
G1 X52.061292 Y163.849769 Z2.433666 E4010.44213 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.930619 matz1=2.433666 note=collision lift
G1 X51.985907 Y163.853472 Z2.395929 E4010.636172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.433666 matz1=2.395929 note=collision lift
G1 X51.202621 Y163.969662 Z2 E4012.802844 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.395929 matz1=2 note=collision lift
G1 X50.928101 Y164.010383 Z2 E4013.531229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X50.682907 Y164.071801 Z2 E4014.215077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X49.890768 Y164.270221 Z2 E4016.557486 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X49.247328 Y164.500448 Z2 E4018.674014 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X48.883899 Y164.630485 Z2 E4019.932401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X47.91719 Y165.087704 Z2 E4023.655975 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X47.878913 Y165.110646 Z2 E4023.818941 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X46.999951 Y165.637476 Z2 E4027.728208 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X46.618231 Y165.920579 Z2 E4029.649858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X46.141016 Y166.274505 Z2 E4032.149098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X45.469815 Y166.882846 Z2 E4036.166766 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X45.348657 Y166.992657 Z2 E4036.914572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X44.630505 Y167.785016 Z2 E4041.805138 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X43.993476 Y168.643951 Z2 E4046.695704 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X43.443704 Y169.56119 Z2 E4051.58627 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.986485 Y170.527899 Z2 E4056.476836 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.626221 Y171.534768 Z2 E4061.367402 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.366383 Y172.572101 Z2 E4066.257968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.209472 Y173.629907 Z2 E4071.148534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.157 Y174.698 Z2 E4076.0391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.209472 Y175.766093 Z2 E4080.929666 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.366383 Y176.823899 Z2 E4085.820232 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.626221 Y177.861232 Z2 E4090.710798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X42.986485 Y178.868101 Z2 E4095.601364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X43.443704 Y179.83481 Z2 E4100.49193 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X43.993476 Y180.752049 Z2 E4105.382496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X44.630505 Y181.610984 Z2 E4110.273062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X45.348657 Y182.403343 Z2 E4115.163628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X46.141016 Y183.121495 Z2 E4120.054194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X46.999951 Y183.758524 Z2 E4124.94476 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X47.91719 Y184.308296 Z2 E4129.835326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X48.883899 Y184.765515 Z2 E4134.725892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X49.890768 Y185.125779 Z2 E4139.616459 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X50.928101 Y185.385617 Z2 E4144.507025 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X51.985907 Y185.542528 Z2 E4149.397591 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X53.054 Y185.595 Z2 E4154.288157 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X54.122093 Y185.542528 Z2 E4159.178723 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X55.179899 Y185.385617 Z2 E4164.069289 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X56.217232 Y185.125779 Z2 E4168.959855 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X57.224101 Y184.765515 Z2 E4173.850421 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X58.19081 Y184.308296 Z2 E4178.740987 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X59.108049 Y183.758524 Z2 E4183.631553 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X59.966984 Y183.121495 Z2 E4188.522119 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X60.759343 Y182.403343 Z2 E4193.412685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X61.477495 Y181.610984 Z2 E4198.303251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X61.642816 Y181.388075 Z2 E4199.572441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X62.114524 Y180.752049 Z2.395929 E4203.621262 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2 matz1=2.395929 note=collision lift
G1 X62.664296 Y179.83481 Z2.930619 E4209.089081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X63.121515 Y178.868101 Z3.46531 E4214.5569 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X63.481779 Y177.861232 Z4 E4220.02472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.46531 matz1=4 note=collision lift
G1 X63.741617 Y176.823899 Z4 E4224.915286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=4 note=collision lift
G1 X63.898528 Y175.766093 Z3.46531 E4230.383105 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=3.46531 note=collision lift
G1 X63.951 Y174.698 Z2.930619 E4235.850924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X63.898528 Y173.629907 Z2.395929 E4241.318743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X63.782338 Y172.846621 Z2 E4245.367564 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.395929 matz1=2 note=collision lift
G1 X63.741617 Y172.572101 Z2 E4246.636754 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X63.481779 Y171.534768 Z2 E4251.52732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X63.121515 Y170.527899 Z2 E4256.417886 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X62.664296 Y169.56119 Z2 E4261.308452 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X62.114524 Y168.643951 Z2 E4266.199018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X62.057385 Y168.566908 Z2 E4266.637685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X61.593425 Y167.941331 Z2.389424 E4270.619993 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2 matz1=2.389424 note=collision lift
G1 X61.477495 Y167.785016 Z2.486731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.389424 matz1=2.486731 note=collision lift
G1 X60.759343 Y166.992657 Z3.021421 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.486731 matz1=3.021421 note=collision lift
G1 X59.966984 Y166.274505 Z3.556112 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.021421 matz1=3.556112 note=collision lift
G1 X59.253723 Y165.745515 Z4.000119 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.556112 matz1=4 note=collision lift
G1 X59.108049 Y165.637476 Z3.909436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=3.909436 note=collision lift
G1 X58.19081 Y165.087704 Z3.374745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.909436 matz1=3.374745 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0015
G0 X58.19081 Y165.087704 Z7.374745 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0016 note=intra-page lift
G0 X54.878559 Y142.758317 Z7.374745 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0016 note=intra-page XY
G0 X54.878559 Y142.758317 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0016 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0016
G1 X55.179899 Y142.713617 Z2 E4270.634141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X56.217232 Y142.453779 Z2 E4270.907793 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X56.335849 Y142.411337 Z2 E4270.962988 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X57.224101 Y142.093515 Z2 E4271.530104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X57.727262 Y141.855538 Z2 E4271.991974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X58.19081 Y141.636296 Z2 E4272.501074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X59.037577 Y141.128764 Z2 E4273.706949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X59.108049 Y141.086524 Z2 E4273.820703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X59.966984 Y140.449495 Z2 E4275.488989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X60.225174 Y140.215485 Z2 E4276.107915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X60.759343 Y139.731343 Z2 E4277.505935 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X61.282539 Y139.154085 Z2 E4279.194872 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X61.477495 Y138.938984 Z2 E4279.871539 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X62.114524 Y138.080049 Z2 E4282.585801 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X62.186661 Y137.959697 Z2 E4282.967818 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X62.664296 Y137.16281 Z2 E4285.648722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X62.908402 Y136.646692 Z2 E4287.426755 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X63.121515 Y136.196101 Z2 E4289.060301 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X63.458928 Y135.253095 Z2 E4292.571682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X63.481779 Y135.189232 Z2 E4292.820539 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X63.741617 Y134.151899 Z2 E4296.929436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X63.79485 Y133.793035 Z2 E4298.4026 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X63.898528 Y133.094093 Z2 E4301.386991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X63.937459 Y132.301638 Z2 E4304.919507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X63.951 Y132.026 Z2 E4306.181594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X63.898528 Y130.957907 Z2 E4311.072161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X63.741617 Y129.900101 Z2 E4315.962727 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X63.481779 Y128.862768 Z2 E4320.853293 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X63.121515 Y127.855899 Z2 E4325.743859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X62.664296 Y126.88919 Z2 E4330.634425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X62.114524 Y125.971951 Z2 E4335.524991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X61.477495 Y125.113016 Z2 E4340.415557 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X60.759343 Y124.320657 Z2 E4345.306123 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X59.966984 Y123.602505 Z2 E4350.196689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X59.108049 Y122.965476 Z2 E4355.087255 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X58.19081 Y122.415704 Z2 E4359.977821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X57.224101 Y121.958485 Z2 E4364.868387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X56.217232 Y121.598221 Z2 E4369.758953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X55.179899 Y121.338383 Z2 E4374.649519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X54.122093 Y121.181472 Z2 E4379.540085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X53.054 Y121.129 Z2 E4384.430651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X51.985907 Y121.181472 Z2 E4389.321217 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X50.928101 Y121.338383 Z2 E4394.211783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X49.890768 Y121.598221 Z2 E4399.102349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X48.883899 Y121.958485 Z2 E4403.992915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X47.91719 Y122.415704 Z2 E4408.883481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X46.999951 Y122.965476 Z2 E4413.774047 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X46.141016 Y123.602505 Z2 E4418.664613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X45.348657 Y124.320657 Z2 E4423.555179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X44.630505 Y125.113016 Z2 E4428.445745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X43.993476 Y125.971951 Z2 E4433.336311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X43.443704 Y126.88919 Z2 E4438.226877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.986485 Y127.855899 Z2 E4443.117443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.626221 Y128.862768 Z2 E4448.008009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.366383 Y129.900101 Z2 E4452.898575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.209472 Y130.957907 Z2 E4457.789141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.157 Y132.026 Z2 E4462.679707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.209472 Y133.094093 Z2 E4467.570274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.366383 Y134.151899 Z2 E4472.46084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.626221 Y135.189232 Z2 E4477.351406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X42.986485 Y136.196101 Z2 E4482.241972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X43.443704 Y137.16281 Z2 E4487.132538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X43.993476 Y138.080049 Z2 E4492.023104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X44.630505 Y138.938984 Z2 E4496.91367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X45.348657 Y139.731343 Z2 E4501.804236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X46.141016 Y140.449495 Z2 E4506.694802 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X46.363925 Y140.614816 Z2 E4507.963992 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X46.999951 Y141.086524 Z2.395929 E4512.012813 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2 matz1=2.395929 note=collision lift
G1 X47.91719 Y141.636296 Z2.930619 E4517.480632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X48.883899 Y142.093515 Z3.46531 E4522.948451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X49.890768 Y142.453779 Z4 E4528.41627 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=3.46531 matz1=4 note=collision lift
G1 X50.38665 Y142.577991 Z4 E4530.754135 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=4 matz1=4 note=collision lift
G1 X50.928101 Y142.713617 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=4 matz1=4 note=collision lift
G1 X51.985907 Y142.870528 Z3.46531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=4 matz1=3.46531 note=collision lift
G1 X53.054 Y142.923 Z2.930619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X54.122093 Y142.870528 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X54.878559 Y142.758317 Z2.013557 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2.395929 matz1=2.013557 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0016
G0 X54.878559 Y142.758317 Z6.013557 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0017 note=intra-page lift
G0 X71.302202 Y131.253445 Z6.013557 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0017 note=intra-page XY
G0 X71.302202 Y131.253445 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0017 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0017
G1 X72.249846 Y132.408154 Z2 E4531.094292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X72.254654 Y132.412099 Z2 E4531.09713 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X73.404555 Y133.355798 Z2 E4532.114763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X73.415524 Y133.361661 Z2 E4532.126115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X74.721952 Y134.059962 Z2 E4533.815548 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X74.739805 Y134.065378 Z2 E4533.841091 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X76.151412 Y134.493584 Z2 E4536.196647 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X76.176167 Y134.496022 Z2 E4536.242057 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X77.638 Y134.64 Z2 E4539.25806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X77.668944 Y134.636952 Z2 E4539.329013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X79.124588 Y134.493584 Z2 E4542.999788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X79.160294 Y134.482753 Z2 E4543.10196 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X80.554048 Y134.059962 Z2 E4547.421829 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X80.592439 Y134.039441 Z2 E4547.560897 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X81.871445 Y133.355798 Z2 E4552.524184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X81.909903 Y133.324237 Z2 E4552.705824 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X83.026154 Y132.408154 Z2 E4558.306854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X83.06166 Y132.364889 Z2 E4558.536741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X83.973798 Y131.253445 Z2 E4564.769837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X84.003114 Y131.1986 Z2 E4565.053649 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X84.677962 Y129.936048 Z2 E4571.60071 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X85.111584 Y128.506588 Z2 E4578.432173 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X85.258 Y127.02 Z2 E4585.263636 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X85.111584 Y125.533412 Z2 E4592.095098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X84.677962 Y124.103952 Z2 E4598.926561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X83.973798 Y122.786555 Z2 E4605.758024 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X83.026154 Y121.631846 Z2 E4612.589486 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X81.871445 Y120.684202 Z2 E4619.420949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X80.554048 Y119.980038 Z2 E4626.252412 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X79.124588 Y119.546416 Z2 E4633.083874 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X77.638 Y119.4 Z2 E4639.915337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X76.151412 Y119.546416 Z2 E4646.7468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X74.721952 Y119.980038 Z2 E4653.578263 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X73.404555 Y120.684202 Z2 E4660.409725 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X72.249846 Y121.631846 Z2 E4667.241188 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X71.302202 Y122.786555 Z2 E4674.072651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X70.598038 Y124.103952 Z2 E4680.904113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X70.164416 Y125.533412 Z2 E4687.735576 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X70.068837 Y126.503841 Z2 E4692.195084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X70.018 Y127.02 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=end-early tail
G1 X70.164416 Y128.506588 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=end-early tail
G1 X70.598038 Y129.936048 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=end-early tail
G1 X71.302202 Y131.253445 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0017
G0 X71.302202 Y131.253445 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0018 note=intra-page lift
G0 X72.316732 Y119.038196 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0018 note=intra-page XY
G0 X72.316732 Y119.038196 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0018 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0018
G1 X73.746908 Y119.156979 Z2 E4692.509041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X73.811801 Y119.157977 Z2 E4692.538079 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X75.311623 Y119.181048 Z2 E4693.567065 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X75.465115 Y119.183409 Z2 E4693.711066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X76.810367 Y119.125675 Z2 E4695.28204 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X77.362 Y119.102 Z2 E4696.086041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X78.302622 Y119.218901 Z2 E4697.683006 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X79.16243 Y119.325758 Z2 E4699.382395 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X79.795865 Y119.339224 Z2 E4700.769963 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X81.295526 Y119.371106 Z2 E4704.542909 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X81.822688 Y119.382313 Z2 E4706.03213 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X82.793554 Y119.322311 Z2 E4709.001846 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X84.290698 Y119.229784 Z2 E4714.146773 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X85.208102 Y119.173086 Z2 E4717.638394 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X85.782996 Y119.090148 Z2 E4719.977691 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X87.267626 Y118.875967 Z2 E4726.494598 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X89.184 Y118.5995 Z2 E4735.349424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X91.351296 Y118.145267 Z2 E4745.4764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X93.615711 Y117.562977 Z2 E4756.169086 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X95.960411 Y116.840308 Z2 E4767.389794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X98.368563 Y115.964938 Z2 E4779.107955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X100.823331 Y114.924544 Z2 E4791.300934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X103.307883 Y113.706805 Z2 E4803.954835 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X105.805384 Y112.299397 Z2 E4817.065293 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X108.299 Y110.69 Z2 E4830.638183 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X105.805384 Y109.080603 Z2 E4844.211072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X103.307883 Y107.673195 Z2 E4857.32153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X100.823331 Y106.455456 Z2 E4869.975432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X98.368563 Y105.415063 Z2 E4882.16841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X95.960411 Y104.539692 Z2 E4893.886572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X93.615711 Y103.817023 Z2 E4905.107279 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X91.351296 Y103.234733 Z2 E4915.799965 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X89.184 Y102.7805 Z2 E4925.926941 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X85.208102 Y102.206914 Z2 E4944.298035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X81.822688 Y101.997688 Z2 E4959.809982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X79.16243 Y102.054242 Z2 E4971.978804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X77.362 Y102.278 Z2 E4980.275997 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X75.465115 Y102.196591 Z2 E4988.958945 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X73.746908 Y102.223021 Z2 E4996.817698 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X72.19961 Y102.351531 Z2 E5003.918272 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X70.815453 Y102.576359 Z2 E5010.331355 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X69.586669 Y102.891744 Z2 E5016.13306 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X68.50549 Y103.291924 Z2 E5021.40541 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X67.564148 Y103.771138 Z2 E5026.236156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X66.754875 Y104.323625 Z2 E5030.717411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X66.069903 Y104.943624 Z2 E5034.94264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X65.501463 Y105.625373 Z2 E5039.002059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X65.041788 Y106.363112 Z2 E5042.977277 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X64.683109 Y107.151078 Z2 E5046.936633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X64.417659 Y107.983511 Z2 E5050.932448 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X64.23767 Y108.85465 Z2 E5055.000548 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X64.103 Y110.69 Z2 E5063.416659 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X64.23767 Y112.52535 Z2 E5071.832771 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X64.417659 Y113.396489 Z2 E5075.900871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X64.683109 Y114.228922 Z2 E5079.896685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X65.041788 Y115.016888 Z2 E5083.856041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X65.501463 Y115.754627 Z2 E5087.83126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X66.069903 Y116.436376 Z2 E5091.890678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X66.754875 Y117.056375 Z2 E5096.115907 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X67.562165 Y117.607508 Z2 E5100.58618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X67.564148 Y117.608862 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
G1 X68.50549 Y118.088076 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
G1 X69.586669 Y118.488256 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
G1 X70.815453 Y118.803641 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
G1 X72.19961 Y119.028469 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
G1 X72.316732 Y119.038196 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0018
G0 X72.316732 Y119.038196 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0019 note=intra-page lift
G0 X63.121515 Y114.860101 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0019 note=intra-page XY
G0 X63.121515 Y114.860101 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0019 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0019
G1 X63.481779 Y113.853232 Z2 E5100.760509 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.586411 Y113.435518 Z2 E5100.929175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.741617 Y112.815899 Z2 E5101.283497 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.867987 Y111.963983 Z2 E5101.958161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.898528 Y111.758093 Z2 E5102.155143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.951 Y110.69 Z2 E5103.375448 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.940084 Y110.467792 Z2 E5103.673136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.898528 Y109.621907 Z2 E5104.944412 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.802699 Y108.97588 Z2 E5106.074102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.741617 Y108.564101 Z2 E5106.862033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.481779 Y107.526768 Z2 E5109.128314 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.47695 Y107.513272 Z2 E5109.161059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X63.121515 Y106.519899 Z2 E5111.743253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X62.931273 Y106.117666 Z2 E5112.934005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X62.664296 Y105.55319 Z2 E5114.70685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X62.214162 Y104.802187 Z2 E5117.392942 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X62.114524 Y104.635951 Z2 E5118.019106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X61.477495 Y103.777016 Z2 E5121.680021 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X61.318463 Y103.601552 Z2 E5122.537869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X60.759343 Y102.984657 Z2 E5125.689594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X60.26481 Y102.536439 Z2 E5128.368787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X59.966984 Y102.266505 Z2 E5130.047825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X59.108049 Y101.629476 Z2 E5134.754716 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X59.08346 Y101.614738 Z2 E5134.885694 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X58.19081 Y101.079704 Z2 E5139.645156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X57.224101 Y100.622485 Z2 E5144.535722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X56.217232 Y100.262221 Z2 E5149.426288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X55.179899 Y100.002383 Z2 E5154.316854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X54.122093 Y99.845472 Z2 E5159.20742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X53.054 Y99.793 Z2 E5164.097986 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X51.985907 Y99.845472 Z2 E5168.988552 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X50.928101 Y100.002383 Z2 E5173.879118 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X49.890768 Y100.262221 Z2 E5178.769685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X48.883899 Y100.622485 Z2 E5183.660251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X47.91719 Y101.079704 Z2 E5188.550817 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X46.999951 Y101.629476 Z2 E5193.441383 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X46.141016 Y102.266505 Z2 E5198.331949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X45.348657 Y102.984657 Z2 E5203.222515 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X44.630505 Y103.777016 Z2 E5208.113081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X43.993476 Y104.635951 Z2 E5213.003647 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X43.443704 Y105.55319 Z2 E5217.894213 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.986485 Y106.519899 Z2 E5222.784779 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.626221 Y107.526768 Z2 E5227.675345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.366383 Y108.564101 Z2 E5232.565911 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.209472 Y109.621907 Z2 E5237.456477 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.157 Y110.69 Z2 E5242.347043 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.209472 Y111.758093 Z2 E5247.237609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.366383 Y112.815899 Z2 E5252.128175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.626221 Y113.853232 Z2 E5257.018741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X42.986485 Y114.860101 Z2 E5261.909307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X43.443704 Y115.82681 Z2 E5266.799873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X43.993476 Y116.744049 Z2 E5271.690439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X44.630505 Y117.602984 Z2 E5276.581005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X45.348657 Y118.395343 Z2 E5281.471571 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X46.141016 Y119.113495 Z2 E5286.362137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X46.363925 Y119.278816 Z2 E5287.631327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X46.999951 Y119.750524 Z2.395929 E5291.680149 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=2 matz1=2.395929 note=collision lift
G1 X47.91719 Y120.300296 Z2.930619 E5297.147968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X48.883899 Y120.757515 Z3.46531 E5302.615787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X49.890768 Y121.117779 Z4 E5308.083606 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=3.46531 matz1=4 note=collision lift
G1 X50.928101 Y121.377617 Z4 E5312.974172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=4 matz1=4 note=collision lift
G1 X51.985907 Y121.534528 Z3.46531 E5318.441991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=4 matz1=3.46531 note=collision lift
G1 X53.054 Y121.587 Z2.930619 E5323.90981 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X54.122093 Y121.534528 Z2.395929 E5329.377629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X54.905379 Y121.418338 Z2 E5333.426451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 matz0=2.395929 matz1=2 note=collision lift
G1 X55.179899 Y121.377617 Z2 E5334.695641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X56.217232 Y121.117779 Z2 E5339.586207 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X57.224101 Y120.757515 Z2 E5344.476773 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X58.19081 Y120.300296 Z2 E5349.367339 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X59.108049 Y119.750524 Z2 E5354.257905 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X59.966984 Y119.113495 Z2 E5359.148471 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X60.224023 Y118.880528 Z2 E5360.734958 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X60.759343 Y118.395343 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
G1 X61.477495 Y117.602984 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
G1 X62.114524 Y116.744049 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
G1 X62.664296 Y115.82681 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
G1 X63.121515 Y114.860101 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0019
G0 X63.121515 Y114.860101 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0020 note=intra-page lift
G0 X57.224101 Y99.421515 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0020 note=intra-page XY
G0 X57.224101 Y99.421515 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0020 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0020
G1 X58.19081 Y98.964296 Z2 E5360.909287 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X58.560165 Y98.742914 Z2 E5361.077953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X59.108049 Y98.414524 Z2 E5361.432275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X59.799802 Y97.901485 Z2 E5362.106939 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X59.966984 Y97.777495 Z2 E5362.303921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X60.759343 Y97.059343 Z2 E5363.524226 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X60.908749 Y96.894498 Z2 E5363.821914 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X61.477495 Y96.266984 Z2 E5365.09319 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X61.866543 Y95.742412 Z2 E5366.22288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X62.114524 Y95.408049 Z2 E5367.010811 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X62.664296 Y94.49081 Z2 E5369.277092 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X62.670424 Y94.477853 Z2 E5369.309837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.121515 Y93.524101 Z2 E5371.892031 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.271415 Y93.105159 Z2 E5373.082783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.481779 Y92.517232 Z2 E5374.855628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.694525 Y91.6679 Z2 E5377.54172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.741617 Y91.479899 Z2 E5378.167884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.898528 Y90.422093 Z2 E5381.828799 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.910148 Y90.185568 Z2 E5382.686647 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.951 Y89.354 Z2 E5385.838372 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.918251 Y88.687375 Z2 E5388.517565 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.898528 Y88.285907 Z2 E5390.196603 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.741617 Y87.228101 Z2 E5394.903493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.734652 Y87.200292 Z2 E5395.034472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X63.481779 Y86.190768 Z2 E5399.793934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X63.121515 Y85.183899 Z2 E5404.6845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X62.664296 Y84.21719 Z2 E5409.575066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X62.114524 Y83.299951 Z2 E5414.465632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X61.477495 Y82.441016 Z2 E5419.356198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X60.759343 Y81.648657 Z2 E5424.246764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X59.966984 Y80.930505 Z2 E5429.13733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X59.108049 Y80.293476 Z2 E5434.027896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X58.19081 Y79.743704 Z2 E5438.918462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X57.224101 Y79.286485 Z2 E5443.809029 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X56.217232 Y78.926221 Z2 E5448.699595 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X55.179899 Y78.666383 Z2 E5453.590161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X54.122093 Y78.509472 Z2 E5458.480727 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X53.054 Y78.457 Z2 E5463.371293 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X51.985907 Y78.509472 Z2 E5468.261859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X50.928101 Y78.666383 Z2 E5473.152425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X49.890768 Y78.926221 Z2 E5478.042991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X48.883899 Y79.286485 Z2 E5482.933557 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X47.91719 Y79.743704 Z2 E5487.824123 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X46.999951 Y80.293476 Z2 E5492.714689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X46.141016 Y80.930505 Z2 E5497.605255 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X45.348657 Y81.648657 Z2 E5502.495821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X44.630505 Y82.441016 Z2 E5507.386387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X43.993476 Y83.299951 Z2 E5512.276953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X43.443704 Y84.21719 Z2 E5517.167519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.986485 Y85.183899 Z2 E5522.058085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.626221 Y86.190768 Z2 E5526.948651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.366383 Y87.228101 Z2 E5531.839217 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.209472 Y88.285907 Z2 E5536.729783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.157 Y89.354 Z2 E5541.620349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.209472 Y90.422093 Z2 E5546.510915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.366383 Y91.479899 Z2 E5551.401481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.626221 Y92.517232 Z2 E5556.292047 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X42.986485 Y93.524101 Z2 E5561.182613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X43.443704 Y94.49081 Z2 E5566.073179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X43.993476 Y95.408049 Z2 E5570.963745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X44.630505 Y96.266984 Z2 E5575.854311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X45.348657 Y97.059343 Z2 E5580.744877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X46.141016 Y97.777495 Z2 E5585.635443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X46.363925 Y97.942816 Z2 E5586.904633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X46.999951 Y98.414524 Z2.395929 E5590.953455 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=2 matz1=2.395929 note=collision lift
G1 X47.91719 Y98.964296 Z2.930619 E5596.421274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X48.883899 Y99.421515 Z3.46531 E5601.889093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X49.890768 Y99.781779 Z4 E5607.356912 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=3.46531 matz1=4 note=collision lift
G1 X50.928101 Y100.041617 Z4 E5612.247478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=4 matz1=4 note=collision lift
G1 X51.985907 Y100.198528 Z3.46531 E5617.715297 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=4 matz1=3.46531 note=collision lift
G1 X52.604835 Y100.228934 Z3.155472 E5620.883736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=3.46531 matz1=3.155472 note=collision lift
G1 X53.054 Y100.251 Z2.930619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=3.155472 matz1=2.930619 note=collision lift
G1 X54.122093 Y100.198528 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X54.905379 Y100.082338 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 matz0=2.395929 matz1=2 note=collision lift
G1 X55.179899 Y100.041617 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=end-early tail
G1 X56.217232 Y99.781779 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=end-early tail
G1 X57.224101 Y99.421515 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0020
G0 X57.224101 Y99.421515 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0021 note=intra-page lift
G0 X70.164416 Y95.846588 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0021 note=intra-page XY
G0 X70.164416 Y95.846588 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0021 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0021
G1 X70.598038 Y97.276048 Z2 E5621.223893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X70.600969 Y97.281532 Z2 E5621.226731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X71.302202 Y98.593445 Z2 E5622.244364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X71.310092 Y98.60306 Z2 E5622.255717 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X72.249846 Y99.748154 Z2 E5623.945149 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X72.264268 Y99.759989 Z2 E5623.970692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X73.404555 Y100.695798 Z2 E5626.326248 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X73.426493 Y100.707524 Z2 E5626.371658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X74.721952 Y101.399962 Z2 E5629.387662 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X74.751707 Y101.408988 Z2 E5629.458615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X76.151412 Y101.833584 Z2 E5633.129389 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X76.188545 Y101.837241 Z2 E5633.231561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X77.638 Y101.98 Z2 E5637.55143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X77.681322 Y101.975733 Z2 E5637.690498 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X79.124588 Y101.833584 Z2 E5642.653785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X79.172196 Y101.819142 Z2 E5642.835425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X80.554048 Y101.399962 Z2 E5648.436455 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X80.603408 Y101.373578 Z2 E5648.666343 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X81.871445 Y100.695798 Z2 E5654.899438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X81.919517 Y100.656347 Z2 E5655.18325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=prime ramp
G1 X83.026154 Y99.748154 Z2 E5661.730311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X83.973798 Y98.593445 Z2 E5668.561774 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X84.677962 Y97.276048 Z2 E5675.393237 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X85.111584 Y95.846588 Z2 E5682.224699 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X85.258 Y94.36 Z2 E5689.056162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X85.111584 Y92.873412 Z2 E5695.887625 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X84.677962 Y91.443952 Z2 E5702.719088 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X83.973798 Y90.126555 Z2 E5709.55055 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X83.026154 Y88.971846 Z2 E5716.382013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X81.871445 Y88.024202 Z2 E5723.213476 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X80.554048 Y87.320038 Z2 E5730.044938 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X79.124588 Y86.886416 Z2 E5736.876401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X77.638 Y86.74 Z2 E5743.707864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X76.151412 Y86.886416 Z2 E5750.539326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X74.721952 Y87.320038 Z2 E5757.370789 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X73.404555 Y88.024202 Z2 E5764.202252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X72.249846 Y88.971846 Z2 E5771.033715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X71.302202 Y90.126555 Z2 E5777.865177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X70.842531 Y90.986538 Z2 E5782.324685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021
G1 X70.598038 Y91.443952 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=end-early tail
G1 X70.164416 Y92.873412 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=end-early tail
G1 X70.018 Y94.36 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=end-early tail
G1 X70.164416 Y95.846588 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0021 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0021
G0 X70.164416 Y95.846588 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0022 note=intra-page lift
G0 X79.841034 Y85.481134 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0022 note=intra-page XY
G0 X79.841034 Y85.481134 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0022 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0022
G1 X80.943052 Y86.498757 Z2 E5782.66768 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X81.344 Y86.869 Z2 E5782.962668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X81.937111 Y87.616541 Z2 E5783.696666 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X82.557973 Y88.399059 Z2 E5784.762421 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X82.905263 Y88.760293 Z2 E5785.411641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X83.944848 Y89.841618 Z2 E5787.812607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X84.545219 Y90.466094 Z2 E5789.511668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X85.018265 Y90.887812 Z2 E5790.899564 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X86.137929 Y91.885988 Z2 E5794.67251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X87.257592 Y92.884163 Z2 E5799.131447 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X87.272855 Y92.89777 Z2 E5799.19697 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X88.448627 Y93.795898 Z2 E5804.276374 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X89.640649 Y94.70644 Z2 E5810.107292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X90.708 Y95.52175 Z2 E5815.910495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X90.838069 Y95.609463 Z2 E5816.624199 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=prime ramp
G1 X92.680612 Y96.852 Z2 E5826.787626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X94.81777 Y98.165699 Z2 E5838.260288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X97.115363 Y99.441307 Z2 E5850.278599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X99.569281 Y100.657281 Z2 E5862.803269 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X102.175415 Y101.79208 Z2 E5875.802698 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X104.929652 Y102.82416 Z2 E5889.253874 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X107.827884 Y103.731981 Z2 E5903.143281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X110.866 Y104.494 Z2 E5917.467777 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X110.103981 Y101.455884 Z2 E5931.792274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X109.19616 Y98.557652 Z2 E5945.68168 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X108.16408 Y95.803415 Z2 E5959.132857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X107.029281 Y93.197281 Z2 E5972.132286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X105.813307 Y90.743363 Z2 E5984.656955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X104.537699 Y88.44577 Z2 E5996.675267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X103.224 Y86.308612 Z2 E6008.147929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X101.89375 Y84.336 Z2 E6019.028811 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X99.26977 Y80.900855 Z2 E6038.79755 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X96.838094 Y78.173219 Z2 E6055.509108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X94.771059 Y76.185973 Z2 E6068.622338 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X93.241 Y74.972 Z2 E6077.554634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X91.853134 Y73.469034 Z2 E6086.910384 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X90.525178 Y72.178475 Z2 E6095.378973 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X89.255285 Y71.09033 Z2 E6103.026983 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X88.041609 Y70.194609 Z2 E6109.925385 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X86.882302 Y69.48132 Z2 E6116.150364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X85.775518 Y68.940471 Z2 E6121.784013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X84.719407 Y68.56207 Z2 E6126.914552 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X83.712125 Y68.336125 Z2 E6131.635594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X82.751823 Y68.252645 Z2 E6136.043875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X81.836654 Y68.301639 Z2 E6140.235181 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X80.964772 Y68.473114 Z2 E6144.298917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X80.134328 Y68.757078 Z2 E6148.312654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X79.343476 Y69.143541 Z2 E6152.33817 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X78.590369 Y69.62251 Z2 E6156.419877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X77.19 Y70.818 Z2 E6164.840444 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X75.99451 Y72.218369 Z2 E6173.261011 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X75.515541 Y72.971476 Z2 E6177.342718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X75.129078 Y73.762328 Z2 E6181.368234 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X74.845114 Y74.592772 Z2 E6185.381971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X74.673639 Y75.464654 Z2 E6189.445707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X74.624645 Y76.379823 Z2 E6193.637013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X74.708125 Y77.340125 Z2 E6198.045295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X74.93407 Y78.347407 Z2 E6202.766337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X75.312471 Y79.403518 Z2 E6207.896875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X75.85332 Y80.510302 Z2 E6213.530524 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X76.566609 Y81.669609 Z2 E6219.755504 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X76.585912 Y81.695764 Z2 E6219.904162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022
G1 X77.46233 Y82.883285 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=end-early tail
G1 X78.550475 Y84.153178 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=end-early tail
G1 X79.841034 Y85.481134 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0022 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0022
G0 X79.841034 Y85.481134 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0023 note=intra-page lift
G0 X74.639048 Y72.390962 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0023 note=intra-page XY
G0 X74.639048 Y72.390962 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0023 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0023
G1 X75.956445 Y71.686798 Z2 E6220.244319 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X75.961252 Y71.682853 Z2 E6220.247157 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X77.111154 Y70.739154 Z2 E6221.26479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X77.119044 Y70.729539 Z2 E6221.276142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X78.058798 Y69.584445 Z2 E6222.965575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X78.067593 Y69.567992 Z2 E6222.991118 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X78.762962 Y68.267048 Z2 E6225.346674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X78.770183 Y68.243244 Z2 E6225.392084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X79.196584 Y66.837588 Z2 E6228.408087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X79.199632 Y66.806644 Z2 E6228.47904 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X79.343 Y65.351 Z2 E6232.149815 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X79.339343 Y65.313867 Z2 E6232.251987 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X79.196584 Y63.864412 Z2 E6236.571856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X79.183947 Y63.822755 Z2 E6236.710924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X78.762962 Y62.434952 Z2 E6241.674211 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X78.73951 Y62.391076 Z2 E6241.855851 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X78.058798 Y61.117555 Z2 E6247.456881 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X78.023292 Y61.07429 Z2 E6247.686768 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X77.111154 Y59.962846 Z2 E6253.919864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X77.063082 Y59.923395 Z2 E6254.203676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=prime ramp
G1 X75.956445 Y59.015202 Z2 E6260.750737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X74.639048 Y58.311038 Z2 E6267.5822 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X73.209588 Y57.877416 Z2 E6274.413663 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X71.723 Y57.731 Z2 E6281.245125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X70.236412 Y57.877416 Z2 E6288.076588 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X68.806952 Y58.311038 Z2 E6294.908051 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X67.489555 Y59.015202 Z2 E6301.739513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X66.334846 Y59.962846 Z2 E6308.570976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X65.387202 Y61.117555 Z2 E6315.402439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X64.683038 Y62.434952 Z2 E6322.233901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X64.249416 Y63.864412 Z2 E6329.065364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X64.103 Y65.351 Z2 E6335.896827 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X64.249416 Y66.837588 Z2 E6342.72829 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X64.683038 Y68.267048 Z2 E6349.559752 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X65.387202 Y69.584445 Z2 E6356.391215 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X66.334846 Y70.739154 Z2 E6363.222678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X67.489555 Y71.686798 Z2 E6370.05414 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X68.806952 Y72.390962 Z2 E6376.885603 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X69.740089 Y72.674026 Z2 E6381.345111 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023
G1 X70.236412 Y72.824584 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=end-early tail
G1 X71.723 Y72.971 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=end-early tail
G1 X73.209588 Y72.824584 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=end-early tail
G1 X74.639048 Y72.390962 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0023 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0023
G0 X74.639048 Y72.390962 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0024 note=intra-page lift
G0 X63.741617 Y70.143899 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0024 note=intra-page XY
G0 X63.741617 Y70.143899 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0024 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0024
G1 X63.898528 Y69.086093 Z2 E6381.51944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.919657 Y68.655992 Z2 E6381.688106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.951 Y68.018 Z2 E6382.042428 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.908741 Y67.157799 Z2 E6382.717092 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.898528 Y66.949907 Z2 E6382.914074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.741617 Y65.892101 Z2 E6384.134379 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.68756 Y65.676292 Z2 E6384.432067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.481779 Y64.854768 Z2 E6385.703343 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.261758 Y64.23985 Z2 E6386.833033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X63.121515 Y63.847899 Z2 E6387.620964 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X62.664296 Y62.88119 Z2 E6389.887245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X62.656927 Y62.868895 Z2 E6389.91999 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X62.114524 Y61.963951 Z2 E6392.502184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X61.849466 Y61.606562 Z2 E6393.692936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X61.477495 Y61.105016 Z2 E6395.465781 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X60.889497 Y60.45626 Z2 E6398.151873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X60.759343 Y60.312657 Z2 E6398.778037 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X59.966984 Y59.594505 Z2 E6402.438952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X59.776776 Y59.453437 Z2 E6403.2968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X59.108049 Y58.957476 Z2 E6406.448525 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X58.535576 Y58.614348 Z2 E6409.127718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X58.19081 Y58.407704 Z2 E6410.806756 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X57.224101 Y57.950485 Z2 E6415.513646 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X57.19711 Y57.940827 Z2 E6415.644625 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=prime ramp
G1 X56.217232 Y57.590221 Z2 E6420.404087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X55.179899 Y57.330383 Z2 E6425.294653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X54.122093 Y57.173472 Z2 E6430.185219 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X53.054 Y57.121 Z2 E6435.075785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X51.985907 Y57.173472 Z2 E6439.966351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X50.928101 Y57.330383 Z2 E6444.856917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X49.890768 Y57.590221 Z2 E6449.747483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X48.883899 Y57.950485 Z2 E6454.638049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X47.91719 Y58.407704 Z2 E6459.528615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X46.999951 Y58.957476 Z2 E6464.419181 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X46.141016 Y59.594505 Z2 E6469.309748 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X45.348657 Y60.312657 Z2 E6474.200314 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X44.630505 Y61.105016 Z2 E6479.09088 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X43.993476 Y61.963951 Z2 E6483.981446 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X43.443704 Y62.88119 Z2 E6488.872012 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.986485 Y63.847899 Z2 E6493.762578 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.626221 Y64.854768 Z2 E6498.653144 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.366383 Y65.892101 Z2 E6503.54371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.209472 Y66.949907 Z2 E6508.434276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.157 Y68.018 Z2 E6513.324842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.209472 Y69.086093 Z2 E6518.215408 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.366383 Y70.143899 Z2 E6523.105974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.626221 Y71.181232 Z2 E6527.99654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X42.986485 Y72.188101 Z2 E6532.887106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X43.443704 Y73.15481 Z2 E6537.777672 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X43.993476 Y74.072049 Z2 E6542.668238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X44.630505 Y74.930984 Z2 E6547.558804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X45.348657 Y75.723343 Z2 E6552.44937 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X46.141016 Y76.441495 Z2 E6557.339936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X46.363925 Y76.606816 Z2 E6558.609126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X46.999951 Y77.078524 Z2.395929 E6562.657948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=2 matz1=2.395929 note=collision lift
G1 X47.91719 Y77.628296 Z2.930619 E6568.125767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X48.883899 Y78.085515 Z3.46531 E6573.593586 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X49.890768 Y78.445779 Z4 E6579.061405 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=3.46531 matz1=4 note=collision lift
G1 X50.928101 Y78.705617 Z4 E6583.951971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=4 matz1=4 note=collision lift
G1 X51.985907 Y78.862528 Z3.46531 E6589.41979 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=4 matz1=3.46531 note=collision lift
G1 X53.054 Y78.915 Z2.930619 E6594.887609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X54.122093 Y78.862528 Z2.395929 E6600.355428 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X54.905379 Y78.746338 Z2 E6604.40425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 matz0=2.395929 matz1=2 note=collision lift
G1 X55.179899 Y78.705617 Z2 E6605.673439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X56.217232 Y78.445779 Z2 E6610.564005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X57.224101 Y78.085515 Z2 E6615.454571 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X58.19081 Y77.628296 Z2 E6620.345138 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X59.108049 Y77.078524 Z2 E6625.235704 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X59.966984 Y76.441495 Z2 E6630.12627 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X60.759343 Y75.723343 Z2 E6635.016836 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X61.477495 Y74.930984 Z2 E6639.907402 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X61.684146 Y74.652347 Z2 E6641.493889 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024
G1 X62.114524 Y74.072049 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=end-early tail
G1 X62.664296 Y73.15481 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=end-early tail
G1 X63.121515 Y72.188101 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=end-early tail
G1 X63.481779 Y71.181232 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=end-early tail
G1 X63.741617 Y70.143899 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0024 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0024
G0 X63.741617 Y70.143899 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0025 note=intra-page lift
G0 X70.102868 Y56.694164 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0025 note=intra-page XY
G0 X70.102868 Y56.694164 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0025 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0025
G1 X70.219899 Y56.749515 Z2 E6641.496444 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X71.226768 Y57.109779 Z2 E6641.712982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X71.518902 Y57.182955 Z2 E6641.836884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X72.264101 Y57.369617 Z2 E6642.278179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X72.987959 Y57.476991 Z2 E6642.86587 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X73.321907 Y57.526528 Z2 E6643.192034 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X74.39 Y57.579 Z2 E6644.454547 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X74.482904 Y57.574436 Z2 E6644.580845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X75.458093 Y57.526528 Z2 E6646.06572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X75.976061 Y57.449695 Z2 E6646.981811 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X76.515899 Y57.369617 Z2 E6648.02555 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X77.441556 Y57.137752 Z2 E6650.068768 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X77.553232 Y57.109779 Z2 E6650.33404 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X78.560101 Y56.749515 Z2 E6652.991187 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X78.845304 Y56.614625 Z2 E6653.841714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X79.52681 Y56.292296 Z2 E6655.996994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X80.166772 Y55.908718 Z2 E6658.300651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X80.444049 Y55.742524 Z2 E6659.351458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X81.302984 Y55.105495 Z2 E6663.054582 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X81.382525 Y55.033403 Z2 E6663.445578 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X82.095343 Y54.387343 Z2 E6667.106364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X82.456621 Y53.988734 Z2 E6669.276496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X82.813495 Y53.594984 Z2 E6671.506804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X83.390482 Y52.817006 Z2 E6675.793403 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=prime ramp
G1 X83.450524 Y52.736049 Z2 E6676.254354 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X84.000296 Y51.81881 Z2 E6681.14492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X84.457515 Y50.852101 Z2 E6686.035486 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X84.817779 Y49.845232 Z2 E6690.926052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X85.077617 Y48.807899 Z2 E6695.816618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X85.234528 Y47.750093 Z2 E6700.707185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X85.287 Y46.682 Z2 E6705.597751 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X85.234528 Y45.613907 Z2 E6710.488317 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X85.077617 Y44.556101 Z2 E6715.378883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X84.817779 Y43.518768 Z2 E6720.269449 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X84.457515 Y42.511899 Z2 E6725.160015 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X84.000296 Y41.54519 Z2 E6730.050581 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X83.450524 Y40.627951 Z2 E6734.941147 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X82.813495 Y39.769016 Z2 E6739.831713 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X82.095343 Y38.976657 Z2 E6744.722279 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X81.302984 Y38.258505 Z2 E6749.612845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X80.444049 Y37.621476 Z2 E6754.503411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X79.52681 Y37.071704 Z2 E6759.393977 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X78.560101 Y36.614485 Z2 E6764.284543 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X77.553232 Y36.254221 Z2 E6769.175109 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X76.515899 Y35.994383 Z2 E6774.065675 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X75.458093 Y35.837472 Z2 E6778.956241 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X74.39 Y35.785 Z2 E6783.846807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X73.321907 Y35.837472 Z2 E6788.737373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X72.264101 Y35.994383 Z2 E6793.627939 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X71.226768 Y36.254221 Z2 E6798.518505 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X70.219899 Y36.614485 Z2 E6803.409071 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X69.25319 Y37.071704 Z2 E6808.299637 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X68.335951 Y37.621476 Z2 E6813.190203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X67.477016 Y38.258505 Z2 E6818.080769 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X66.684657 Y38.976657 Z2 E6822.971335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X65.966505 Y39.769016 Z2 E6827.861901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X65.329476 Y40.627951 Z2 E6832.752467 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X64.779704 Y41.54519 Z2 E6837.643033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X64.322485 Y42.511899 Z2 E6842.533599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X63.962221 Y43.518768 Z2 E6847.424165 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X63.702383 Y44.556101 Z2 E6852.314731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X63.545472 Y45.613907 Z2 E6857.205298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X63.493 Y46.682 Z2 E6862.095864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X63.545472 Y47.750093 Z2 E6866.98643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X63.702383 Y48.807899 Z2 E6871.876996 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X63.962221 Y49.845232 Z2 E6876.767562 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X64.322485 Y50.852101 Z2 E6881.658128 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X64.779704 Y51.81881 Z2 E6886.548694 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X65.329476 Y52.736049 Z2 E6891.43926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X65.966505 Y53.594984 Z2 E6896.329826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X66.112532 Y53.756099 Z2 E6897.324258 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025
G1 X66.684657 Y54.387343 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=end-early tail
G1 X67.477016 Y55.105495 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=end-early tail
G1 X68.335951 Y55.742524 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=end-early tail
G1 X69.25319 Y56.292296 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=end-early tail
G1 X70.102868 Y56.694164 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0025 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0025
G0 X70.102868 Y56.694164 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0026 note=intra-page lift
G0 X62.480484 Y52.125483 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0026 note=intra-page XY
G0 X62.480484 Y52.125483 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0026 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0026
G1 X62.664296 Y51.81881 Z2.286456 E6897.356254 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2 matz1=2.286456 note=collision lift
G1 X63.011935 Y51.083789 Z2.937888 E6897.667253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.286456 matz1=2.937888 note=collision lift
G1 X63.121515 Y50.852101 Z3.143228 E6897.833884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.937888 matz1=3.143228 note=collision lift
G1 X63.429544 Y49.991218 Z3.875777 E6898.696238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.143228 matz1=3.875777 note=collision lift
G1 X63.481779 Y49.845232 Z4 E6898.883975 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.875777 matz1=4 note=collision lift
G1 X63.741617 Y48.807899 Z4 E6900.101193 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=4 matz1=4 note=collision lift
G1 X63.772057 Y48.602688 Z3.896272 E6900.411214 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=4 matz1=3.896272 note=collision lift
G1 X63.898528 Y47.750093 Z3.46531 E6901.874901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.896272 matz1=3.46531 note=collision lift
G1 X63.922067 Y47.270954 Z3.225451 E6902.81218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.46531 matz1=3.225451 note=collision lift
G1 X63.951 Y46.682 Z2.930619 E6904.084433 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.225451 matz1=2.930619 note=collision lift
G1 X63.914102 Y45.930929 Z2.554631 E6905.899136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.930619 matz1=2.554631 note=collision lift
G1 X63.898528 Y45.613907 Z2.395929 E6906.729789 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.554631 matz1=2.395929 note=collision lift
G1 X63.782338 Y44.830621 Z2 E6908.96947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.395929 matz1=2 note=collision lift
G1 X63.744217 Y44.573625 Z2 E6909.672083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X63.741617 Y44.556101 Z2 E6909.720742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X63.481779 Y43.518768 Z2 E6912.835187 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X63.342676 Y43.130001 Z2 E6914.13102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X63.121515 Y42.511899 Z2 E6916.29829 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X62.760863 Y41.749363 Z2 E6919.275947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X62.664296 Y41.54519 Z2 E6920.110052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X62.114524 Y40.627951 Z2 E6924.270472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X61.992548 Y40.463486 Z2 E6925.106864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X61.477495 Y39.769016 Z2 E6928.779551 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X61.0508 Y39.298231 Z2 E6931.623772 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 note=prime ramp
G1 X60.759343 Y38.976657 Z2 E6933.608575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X59.966984 Y38.258505 Z2 E6938.499141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X59.108049 Y37.621476 Z2 E6943.389707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X58.19081 Y37.071704 Z2 E6948.280273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X57.224101 Y36.614485 Z2 E6953.170839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X56.217232 Y36.254221 Z2 E6958.061405 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X55.179899 Y35.994383 Z2 E6962.951971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X54.122093 Y35.837472 Z2 E6967.842537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X53.054 Y35.785 Z2 E6972.733103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X51.985907 Y35.837472 Z2 E6977.623669 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X50.928101 Y35.994383 Z2 E6982.514235 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X49.890768 Y36.254221 Z2 E6987.404801 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X48.883899 Y36.614485 Z2 E6992.295367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X47.91719 Y37.071704 Z2 E6997.185933 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X46.999951 Y37.621476 Z2 E7002.0765 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X46.141016 Y38.258505 Z2 E7006.967066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X45.348657 Y38.976657 Z2 E7011.857632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X44.630505 Y39.769016 Z2 E7016.748198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X43.993476 Y40.627951 Z2 E7021.638764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X43.443704 Y41.54519 Z2 E7026.52933 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.986485 Y42.511899 Z2 E7031.419896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.626221 Y43.518768 Z2 E7036.310462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.366383 Y44.556101 Z2 E7041.201028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.209472 Y45.613907 Z2 E7046.091594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.157 Y46.682 Z2 E7050.98216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.209472 Y47.750093 Z2 E7055.872726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.366383 Y48.807899 Z2 E7060.763292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.626221 Y49.845232 Z2 E7065.653858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X42.986485 Y50.852101 Z2 E7070.544424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X43.443704 Y51.81881 Z2 E7075.43499 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X43.993476 Y52.736049 Z2 E7080.325556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X44.630505 Y53.594984 Z2 E7085.216122 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X45.348657 Y54.387343 Z2 E7090.106688 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X46.141016 Y55.105495 Z2 E7094.997254 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X46.363925 Y55.270816 Z2 E7096.266444 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X46.999951 Y55.742524 Z2.395929 E7100.315266 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2 matz1=2.395929 note=collision lift
G1 X47.91719 Y56.292296 Z2.930619 E7105.783085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X48.883899 Y56.749515 Z3.46531 E7111.250904 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X49.890768 Y57.109779 Z4 E7116.718723 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.46531 matz1=4 note=collision lift
G1 X50.928101 Y57.369617 Z4 E7121.609289 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=4 matz1=4 note=collision lift
G1 X51.985907 Y57.526528 Z3.46531 E7127.077108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=4 matz1=3.46531 note=collision lift
G1 X53.054 Y57.579 Z2.930619 E7132.544927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X54.122093 Y57.526528 Z2.395929 E7138.012746 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X54.905379 Y57.410338 Z2 E7142.061568 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.395929 matz1=2 note=collision lift
G1 X55.179899 Y57.369617 Z2 E7143.330757 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X56.217232 Y57.109779 Z2 E7148.221323 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X57.224101 Y56.749515 Z2 E7153.11189 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X58.19081 Y56.292296 Z2 E7158.002456 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X58.883056 Y55.87738 Z2 E7161.693397 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026
G1 X59.108049 Y55.742524 Z2.131156 E7163.034618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2 matz1=2.131156 note=collision lift
G1 X59.523491 Y55.434412 Z2.38977 E7165.679243 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.131156 matz1=2.38977 note=collision lift
G1 X59.966984 Y55.105495 Z2.665847 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.38977 matz1=2.665847 note=collision lift
G1 X60.759343 Y54.387343 Z3.200537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=2.665847 matz1=3.200537 note=collision lift
G1 X61.477495 Y53.594984 Z3.735228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.200537 matz1=3.735228 note=collision lift
G1 X61.793062 Y53.16949 Z4.000099 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.735228 matz1=4 note=collision lift
G1 X62.114524 Y52.736049 Z3.73028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=4 matz1=3.73028 note=collision lift
G1 X62.480484 Y52.125483 Z3.37436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0026 matz0=3.73028 matz1=3.37436 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0026
G0 X62.480484 Y52.125483 Z7.37436 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0027 note=intra-page lift
G0 X85.034237 Y48.779949 Z7.37436 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0027 note=intra-page XY
G0 X85.034237 Y48.779949 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0027 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0027
G1 X85.038383 Y48.807899 Z2 E7165.679365 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X85.298221 Y49.845232 Z2 E7165.862907 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X85.433773 Y50.224075 Z2 E7166.022239 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X85.658485 Y50.852101 Z2 E7166.395107 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X86.014631 Y51.605109 Z2 E7167.051224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X86.115704 Y51.81881 Z2 E7167.275966 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X86.665476 Y52.736049 Z2 E7168.505483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X86.781173 Y52.892048 Z2 E7168.7662 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X87.302505 Y53.594984 Z2 E7170.083659 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X87.722122 Y54.057959 Z2 E7171.167166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X88.020657 Y54.387343 Z2 E7172.010493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X88.802701 Y55.096145 Z2 E7174.254122 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X88.813016 Y55.105495 Z2 E7174.285986 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X89.671951 Y55.742524 Z2 E7176.910137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X90.029364 Y55.956749 Z2 E7178.027069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X90.58919 Y56.292296 Z2 E7179.882947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X91.355155 Y56.65457 Z2 E7182.486005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X91.555899 Y56.749515 Z2 E7183.204416 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X92.562768 Y57.109779 Z2 E7186.874543 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X92.765072 Y57.160453 Z2 E7187.630933 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X93.600101 Y57.369617 Z2 E7190.893328 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X94.232356 Y57.463403 Z2 E7193.46185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X94.657907 Y57.526528 Z2 E7195.260772 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X95.726 Y57.579 Z2 E7199.976875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X95.726411 Y57.57898 Z2 E7199.978758 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=prime ramp
G1 X96.794093 Y57.526528 Z2 E7204.867441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X97.851899 Y57.369617 Z2 E7209.758007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X98.889232 Y57.109779 Z2 E7214.648573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X99.896101 Y56.749515 Z2 E7219.539139 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X100.86281 Y56.292296 Z2 E7224.429705 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X101.780049 Y55.742524 Z2 E7229.320271 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X102.638984 Y55.105495 Z2 E7234.210837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X103.431343 Y54.387343 Z2 E7239.101403 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X104.149495 Y53.594984 Z2 E7243.991969 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X104.786524 Y52.736049 Z2 E7248.882535 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X105.336296 Y51.81881 Z2 E7253.773101 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X105.793515 Y50.852101 Z2 E7258.663667 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X106.153779 Y49.845232 Z2 E7263.554233 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X106.413617 Y48.807899 Z2 E7268.444799 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X106.570528 Y47.750093 Z2 E7273.335365 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X106.623 Y46.682 Z2 E7278.225931 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X106.570528 Y45.613907 Z2 E7283.116497 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X106.413617 Y44.556101 Z2 E7288.007063 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X106.153779 Y43.518768 Z2 E7292.897629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X105.793515 Y42.511899 Z2 E7297.788195 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X105.336296 Y41.54519 Z2 E7302.678761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X104.786524 Y40.627951 Z2 E7307.569327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X104.149495 Y39.769016 Z2 E7312.459894 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X103.431343 Y38.976657 Z2 E7317.35046 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X102.638984 Y38.258505 Z2 E7322.241026 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X101.780049 Y37.621476 Z2 E7327.131592 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X100.86281 Y37.071704 Z2 E7332.022158 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X99.896101 Y36.614485 Z2 E7336.912724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X98.889232 Y36.254221 Z2 E7341.80329 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X97.851899 Y35.994383 Z2 E7346.693856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X96.794093 Y35.837472 Z2 E7351.584422 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X95.726 Y35.785 Z2 E7356.474988 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X94.657907 Y35.837472 Z2 E7361.365554 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X93.600101 Y35.994383 Z2 E7366.25612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X92.562768 Y36.254221 Z2 E7371.146686 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X91.555899 Y36.614485 Z2 E7376.037252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X90.58919 Y37.071704 Z2 E7380.927818 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X89.671951 Y37.621476 Z2 E7385.818384 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X88.813016 Y38.258505 Z2 E7390.70895 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X88.020657 Y38.976657 Z2 E7395.599516 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X87.302505 Y39.769016 Z2 E7400.490082 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X87.137184 Y39.991925 Z2 E7401.759272 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027
G1 X86.665476 Y40.627951 Z2.395929 E7405.808094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=2 matz1=2.395929 note=collision lift
G1 X86.115704 Y41.54519 Z2.930619 E7411.275913 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X85.658485 Y42.511899 Z3.46531 E7416.743732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X85.298221 Y43.518768 Z4 E7422.211551 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=3.46531 matz1=4 note=collision lift
G1 X85.106076 Y44.285854 Z4 E7425.828021 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=4 matz1=4 note=collision lift
G1 X85.038383 Y44.556101 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=4 matz1=4 note=collision lift
G1 X84.881472 Y45.613907 Z3.46531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=4 matz1=3.46531 note=collision lift
G1 X84.829 Y46.682 Z2.930619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X84.881472 Y47.750093 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X84.997662 Y48.533379 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 matz0=2.395929 matz1=2 note=collision lift
G1 X85.034237 Y48.779949 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0027 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0027
G0 X85.034237 Y48.779949 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0028 note=intra-page lift
G0 X96.498555 Y64.930202 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0028 note=intra-page XY
G0 X96.498555 Y64.930202 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0028 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0028
G1 X95.343846 Y65.877846 Z2 E7426.168178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X95.339901 Y65.882654 Z2 E7426.171017 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X94.396202 Y67.032555 Z2 E7427.18865 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X94.390339 Y67.043524 Z2 E7427.200002 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.692038 Y68.349952 Z2 E7428.889435 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.686622 Y68.367805 Z2 E7428.914978 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.258416 Y69.779412 Z2 E7431.270534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.255978 Y69.804167 Z2 E7431.315944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.112 Y71.266 Z2 E7434.331947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.115048 Y71.296944 Z2 E7434.4029 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.258416 Y72.752588 Z2 E7438.073674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.269247 Y72.788294 Z2 E7438.175847 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.692038 Y74.182048 Z2 E7442.495716 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X93.712559 Y74.220439 Z2 E7442.634783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X94.396202 Y75.499445 Z2 E7447.598071 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X94.427763 Y75.537903 Z2 E7447.779711 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X95.343846 Y76.654154 Z2 E7453.38074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X95.387111 Y76.68966 Z2 E7453.610628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X96.498555 Y77.601798 Z2 E7459.843724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X96.5534 Y77.631114 Z2 E7460.127536 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=prime ramp
G1 X97.815952 Y78.305962 Z2 E7466.674597 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X99.245412 Y78.739584 Z2 E7473.50606 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X100.732 Y78.886 Z2 E7480.337522 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X102.218588 Y78.739584 Z2 E7487.168985 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X103.648048 Y78.305962 Z2 E7494.000448 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X104.965445 Y77.601798 Z2 E7500.83191 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X106.120154 Y76.654154 Z2 E7507.663373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X107.067798 Y75.499445 Z2 E7514.494836 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X107.771962 Y74.182048 Z2 E7521.326298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X108.205584 Y72.752588 Z2 E7528.157761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X108.352 Y71.266 Z2 E7534.989224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X108.205584 Y69.779412 Z2 E7541.820686 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X107.771962 Y68.349952 Z2 E7548.652149 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X107.067798 Y67.032555 Z2 E7555.483612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X106.120154 Y65.877846 Z2 E7562.315075 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X104.965445 Y64.930202 Z2 E7569.146537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X103.648048 Y64.226038 Z2 E7575.978 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X102.218588 Y63.792416 Z2 E7582.809463 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X101.248159 Y63.696837 Z2 E7587.268971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028
G1 X100.732 Y63.646 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=end-early tail
G1 X99.245412 Y63.792416 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=end-early tail
G1 X97.815952 Y64.226038 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=end-early tail
G1 X96.498555 Y64.930202 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0028 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0028
G0 X96.498555 Y64.930202 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0029 note=intra-page lift
G0 X108.713804 Y65.944732 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0029 note=intra-page XY
G0 X108.713804 Y65.944732 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0029 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0029
G1 X108.595021 Y67.374908 Z2 E7587.582927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.594023 Y67.439801 Z2 E7587.611966 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.570952 Y68.939623 Z2 E7588.640951 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.568591 Y69.093115 Z2 E7588.784952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.626325 Y70.438367 Z2 E7590.355927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.65 Y70.99 Z2 E7591.159927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.533099 Y71.930622 Z2 E7592.756893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.426242 Y72.79043 Z2 E7594.456281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.412776 Y73.423865 Z2 E7595.843849 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.380894 Y74.923526 Z2 E7599.616796 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.369688 Y75.450688 Z2 E7601.106017 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.429689 Y76.421554 Z2 E7604.075733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.522216 Y77.918698 Z2 E7609.22066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.578914 Y78.836102 Z2 E7612.71228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.661852 Y79.410996 Z2 E7615.051577 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X108.876033 Y80.895626 Z2 E7621.568485 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=prime ramp
G1 X109.1525 Y82.812 Z2 E7630.423311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X109.606733 Y84.979296 Z2 E7640.550286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X110.189023 Y87.243711 Z2 E7651.242973 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X110.911692 Y89.588411 Z2 E7662.46368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X111.787063 Y91.996563 Z2 E7674.181842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X112.827456 Y94.451331 Z2 E7686.37482 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X114.045195 Y96.935883 Z2 E7699.028722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X115.452603 Y99.433384 Z2 E7712.13918 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X117.062 Y101.927 Z2 E7725.712069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X118.671397 Y99.433384 Z2 E7739.284959 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X120.078805 Y96.935883 Z2 E7752.395417 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X121.296544 Y94.451331 Z2 E7765.049318 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X122.336938 Y91.996563 Z2 E7777.242297 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X123.212308 Y89.588411 Z2 E7788.960458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X123.934977 Y87.243711 Z2 E7800.181166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X124.517267 Y84.979296 Z2 E7810.873852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X124.9715 Y82.812 Z2 E7821.000828 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X125.545086 Y78.836102 Z2 E7839.371921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X125.754313 Y75.450688 Z2 E7854.883868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X125.697758 Y72.79043 Z2 E7867.052691 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X125.474 Y70.99 Z2 E7875.349884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X125.555409 Y69.093115 Z2 E7884.032832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X125.528979 Y67.374908 Z2 E7891.891585 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X125.400469 Y65.82761 Z2 E7898.992159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X125.175641 Y64.443453 Z2 E7905.405241 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X124.860256 Y63.214669 Z2 E7911.206947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X124.460076 Y62.13349 Z2 E7916.479296 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X123.980862 Y61.192148 Z2 E7921.310043 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X123.428375 Y60.382875 Z2 E7925.791298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X122.808376 Y59.697903 Z2 E7930.016527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X122.126627 Y59.129463 Z2 E7934.075946 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X121.388888 Y58.669788 Z2 E7938.051164 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X120.600922 Y58.311109 Z2 E7942.01052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X119.768489 Y58.045659 Z2 E7946.006334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X118.89735 Y57.86567 Z2 E7950.074434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X117.062 Y57.731 Z2 E7958.490546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X115.22665 Y57.86567 Z2 E7966.906658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X114.355511 Y58.045659 Z2 E7970.974757 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X113.523078 Y58.311109 Z2 E7974.970572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X112.735112 Y58.669788 Z2 E7978.929928 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X111.997373 Y59.129463 Z2 E7982.905146 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X111.315624 Y59.697903 Z2 E7986.964565 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X110.695625 Y60.382875 Z2 E7991.189794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X110.144492 Y61.190165 Z2 E7995.660067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029
G1 X110.143138 Y61.192148 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=end-early tail
G1 X109.663924 Y62.13349 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=end-early tail
G1 X109.263744 Y63.214669 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=end-early tail
G1 X108.948359 Y64.443453 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=end-early tail
G1 X108.723531 Y65.82761 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=end-early tail
G1 X108.713804 Y65.944732 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0029 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0029
G0 X108.713804 Y65.944732 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0030 note=intra-page lift
G0 X112.891899 Y56.749515 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0030 note=intra-page XY
G0 X112.891899 Y56.749515 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0030 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0030
G1 X113.898768 Y57.109779 Z2 E7995.834396 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X114.316482 Y57.214411 Z2 E7996.003062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X114.936101 Y57.369617 Z2 E7996.357384 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X115.788017 Y57.495987 Z2 E7997.032047 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X115.993907 Y57.526528 Z2 E7997.22903 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X117.062 Y57.579 Z2 E7998.449335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X117.284208 Y57.568084 Z2 E7998.747023 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X118.130093 Y57.526528 Z2 E8000.018298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X118.77612 Y57.430699 Z2 E8001.147989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X119.187899 Y57.369617 Z2 E8001.93592 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X120.225232 Y57.109779 Z2 E8004.2022 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X120.238728 Y57.10495 Z2 E8004.234945 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X121.232101 Y56.749515 Z2 E8006.817139 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X121.634334 Y56.559273 Z2 E8008.007892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X122.19881 Y56.292296 Z2 E8009.780737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X122.949813 Y55.842162 Z2 E8012.466829 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X123.116049 Y55.742524 Z2 E8013.092993 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X123.974984 Y55.105495 Z2 E8016.753907 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X124.150448 Y54.946463 Z2 E8017.611756 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X124.767343 Y54.387343 Z2 E8020.76348 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X125.215561 Y53.89281 Z2 E8023.442673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X125.485495 Y53.594984 Z2 E8025.121712 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X126.122524 Y52.736049 Z2 E8029.828602 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X126.137262 Y52.71146 Z2 E8029.959581 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=prime ramp
G1 X126.672296 Y51.81881 Z2 E8034.719043 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.129515 Y50.852101 Z2 E8039.609609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.489779 Y49.845232 Z2 E8044.500175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.749617 Y48.807899 Z2 E8049.390741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.906528 Y47.750093 Z2 E8054.281307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.959 Y46.682 Z2 E8059.171873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.906528 Y45.613907 Z2 E8064.062439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.749617 Y44.556101 Z2 E8068.953005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.489779 Y43.518768 Z2 E8073.843571 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X127.129515 Y42.511899 Z2 E8078.734137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X126.672296 Y41.54519 Z2 E8083.624703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X126.122524 Y40.627951 Z2 E8088.515269 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X125.485495 Y39.769016 Z2 E8093.405835 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X124.767343 Y38.976657 Z2 E8098.296401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X123.974984 Y38.258505 Z2 E8103.186967 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X123.116049 Y37.621476 Z2 E8108.077533 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X122.19881 Y37.071704 Z2 E8112.968099 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X121.232101 Y36.614485 Z2 E8117.858665 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X120.225232 Y36.254221 Z2 E8122.749231 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X119.187899 Y35.994383 Z2 E8127.639797 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X118.130093 Y35.837472 Z2 E8132.530363 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X117.062 Y35.785 Z2 E8137.42093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X115.993907 Y35.837472 Z2 E8142.311496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X114.936101 Y35.994383 Z2 E8147.202062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X113.898768 Y36.254221 Z2 E8152.092628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X112.891899 Y36.614485 Z2 E8156.983194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X111.92519 Y37.071704 Z2 E8161.87376 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X111.007951 Y37.621476 Z2 E8166.764326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X110.149016 Y38.258505 Z2 E8171.654892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X109.356657 Y38.976657 Z2 E8176.545458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X108.638505 Y39.769016 Z2 E8181.436024 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X108.473184 Y39.991925 Z2 E8182.705214 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X108.001476 Y40.627951 Z2.395929 E8186.754035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=2 matz1=2.395929 note=collision lift
G1 X107.451704 Y41.54519 Z2.930619 E8192.221854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X106.994485 Y42.511899 Z3.46531 E8197.689673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X106.634221 Y43.518768 Z4 E8203.157492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=3.46531 matz1=4 note=collision lift
G1 X106.374383 Y44.556101 Z4 E8208.048058 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=4 matz1=4 note=collision lift
G1 X106.217472 Y45.613907 Z3.46531 E8213.515878 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=4 matz1=3.46531 note=collision lift
G1 X106.165 Y46.682 Z2.930619 E8218.983697 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X106.217472 Y47.750093 Z2.395929 E8224.451516 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X106.333662 Y48.533379 Z2 E8228.500337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 matz0=2.395929 matz1=2 note=collision lift
G1 X106.374383 Y48.807899 Z2 E8229.769527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X106.634221 Y49.845232 Z2 E8234.660093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X106.994485 Y50.852101 Z2 E8239.550659 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X107.451704 Y51.81881 Z2 E8244.441225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X108.001476 Y52.736049 Z2 E8249.331791 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X108.638505 Y53.594984 Z2 E8254.222357 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X108.871472 Y53.852023 Z2 E8255.808845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030
G1 X109.356657 Y54.387343 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=end-early tail
G1 X110.149016 Y55.105495 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=end-early tail
G1 X111.007951 Y55.742524 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=end-early tail
G1 X111.92519 Y56.292296 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=end-early tail
G1 X112.891899 Y56.749515 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0030 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0030
G0 X112.891899 Y56.749515 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0031 note=intra-page lift
G0 X128.330485 Y50.852101 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0031 note=intra-page XY
G0 X128.330485 Y50.852101 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0031 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0031
G1 X128.787704 Y51.81881 Z2 E8255.983174 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X129.009086 Y52.188165 Z2 E8256.15184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X129.337476 Y52.736049 Z2 E8256.506162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X129.850515 Y53.427802 Z2 E8257.180825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X129.974505 Y53.594984 Z2 E8257.377808 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X130.692657 Y54.387343 Z2 E8258.598113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X130.857502 Y54.536749 Z2 E8258.895801 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X131.485016 Y55.105495 Z2 E8260.167076 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X132.009588 Y55.494543 Z2 E8261.296767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X132.343951 Y55.742524 Z2 E8262.084698 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X133.26119 Y56.292296 Z2 E8264.350978 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X133.274147 Y56.298424 Z2 E8264.383723 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X134.227899 Y56.749515 Z2 E8266.965917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X134.646841 Y56.899415 Z2 E8268.15667 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X135.234768 Y57.109779 Z2 E8269.929515 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X136.0841 Y57.322525 Z2 E8272.615607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X136.272101 Y57.369617 Z2 E8273.241771 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X137.329907 Y57.526528 Z2 E8276.902685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X137.566432 Y57.538148 Z2 E8277.760534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X138.398 Y57.579 Z2 E8280.912258 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X139.064625 Y57.546251 Z2 E8283.591451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X139.466093 Y57.526528 Z2 E8285.27049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X140.523899 Y57.369617 Z2 E8289.97738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X140.551708 Y57.362652 Z2 E8290.108359 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=prime ramp
G1 X141.561232 Y57.109779 Z2 E8294.867821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X142.568101 Y56.749515 Z2 E8299.758387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X143.53481 Y56.292296 Z2 E8304.648953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X144.452049 Y55.742524 Z2 E8309.539519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X145.310984 Y55.105495 Z2 E8314.430085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X146.103343 Y54.387343 Z2 E8319.320651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X146.821495 Y53.594984 Z2 E8324.211217 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X147.458524 Y52.736049 Z2 E8329.101783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X148.008296 Y51.81881 Z2 E8333.992349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X148.465515 Y50.852101 Z2 E8338.882915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X148.825779 Y49.845232 Z2 E8343.773481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X149.085617 Y48.807899 Z2 E8348.664047 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X149.242528 Y47.750093 Z2 E8353.554613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X149.295 Y46.682 Z2 E8358.445179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X149.242528 Y45.613907 Z2 E8363.335745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X149.085617 Y44.556101 Z2 E8368.226311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X148.825779 Y43.518768 Z2 E8373.116877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X148.465515 Y42.511899 Z2 E8378.007443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X148.008296 Y41.54519 Z2 E8382.898009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X147.458524 Y40.627951 Z2 E8387.788575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X146.821495 Y39.769016 Z2 E8392.679141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X146.103343 Y38.976657 Z2 E8397.569708 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X145.310984 Y38.258505 Z2 E8402.460274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X144.452049 Y37.621476 Z2 E8407.35084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X143.53481 Y37.071704 Z2 E8412.241406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X142.568101 Y36.614485 Z2 E8417.131972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X141.561232 Y36.254221 Z2 E8422.022538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X140.523899 Y35.994383 Z2 E8426.913104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X139.466093 Y35.837472 Z2 E8431.80367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X138.398 Y35.785 Z2 E8436.694236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X137.329907 Y35.837472 Z2 E8441.584802 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X136.272101 Y35.994383 Z2 E8446.475368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X135.234768 Y36.254221 Z2 E8451.365934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X134.227899 Y36.614485 Z2 E8456.2565 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X133.26119 Y37.071704 Z2 E8461.147066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X132.343951 Y37.621476 Z2 E8466.037632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X131.485016 Y38.258505 Z2 E8470.928198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X130.692657 Y38.976657 Z2 E8475.818764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X129.974505 Y39.769016 Z2 E8480.70933 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X129.809184 Y39.991925 Z2 E8481.97852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031
G1 X129.337476 Y40.627951 Z2.395929 E8486.027342 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=2 matz1=2.395929 note=collision lift
G1 X128.787704 Y41.54519 Z2.930619 E8491.495161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X128.330485 Y42.511899 Z3.46531 E8496.96298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X127.970221 Y43.518768 Z4 E8502.430799 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=3.46531 matz1=4 note=collision lift
G1 X127.710383 Y44.556101 Z4 E8507.321365 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=4 matz1=4 note=collision lift
G1 X127.553472 Y45.613907 Z3.46531 E8512.789184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=4 matz1=3.46531 note=collision lift
G1 X127.523066 Y46.232835 Z3.155472 E8515.957623 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=3.46531 matz1=3.155472 note=collision lift
G1 X127.501 Y46.682 Z2.930619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=3.155472 matz1=2.930619 note=collision lift
G1 X127.553472 Y47.750093 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X127.669662 Y48.533379 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 matz0=2.395929 matz1=2 note=collision lift
G1 X127.710383 Y48.807899 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=end-early tail
G1 X127.970221 Y49.845232 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=end-early tail
G1 X128.330485 Y50.852101 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0031 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0031
G0 X128.330485 Y50.852101 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0032 note=intra-page lift
G0 X131.905412 Y63.792416 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0032 note=intra-page XY
G0 X131.905412 Y63.792416 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0032 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0032
G1 X130.475952 Y64.226038 Z2 E8516.29778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X130.470468 Y64.228969 Z2 E8516.300618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X129.158555 Y64.930202 Z2 E8517.318251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X129.14894 Y64.938092 Z2 E8517.329603 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X128.003846 Y65.877846 Z2 E8519.019036 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X127.992011 Y65.892268 Z2 E8519.044579 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X127.056202 Y67.032555 Z2 E8521.400135 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X127.044476 Y67.054493 Z2 E8521.445545 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X126.352038 Y68.349952 Z2 E8524.461548 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X126.343012 Y68.379707 Z2 E8524.532501 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X125.918416 Y69.779412 Z2 E8528.203275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X125.914759 Y69.816545 Z2 E8528.305448 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X125.772 Y71.266 Z2 E8532.625317 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X125.776267 Y71.309322 Z2 E8532.764385 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X125.918416 Y72.752588 Z2 E8537.727672 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X125.932858 Y72.800196 Z2 E8537.909312 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X126.352038 Y74.182048 Z2 E8543.510341 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X126.378422 Y74.231408 Z2 E8543.740229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X127.056202 Y75.499445 Z2 E8549.973325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X127.095653 Y75.547517 Z2 E8550.257137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=prime ramp
G1 X128.003846 Y76.654154 Z2 E8556.804198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X129.158555 Y77.601798 Z2 E8563.635661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X130.475952 Y78.305962 Z2 E8570.467123 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X131.905412 Y78.739584 Z2 E8577.298586 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X133.392 Y78.886 Z2 E8584.130049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X134.878588 Y78.739584 Z2 E8590.961511 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X136.308048 Y78.305962 Z2 E8597.792974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X137.625445 Y77.601798 Z2 E8604.624437 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X138.780154 Y76.654154 Z2 E8611.4559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X139.727798 Y75.499445 Z2 E8618.287362 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X140.431962 Y74.182048 Z2 E8625.118825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X140.865584 Y72.752588 Z2 E8631.950288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X141.012 Y71.266 Z2 E8638.78175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X140.865584 Y69.779412 Z2 E8645.613213 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X140.431962 Y68.349952 Z2 E8652.444676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X139.727798 Y67.032555 Z2 E8659.276138 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X138.780154 Y65.877846 Z2 E8666.107601 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X137.625445 Y64.930202 Z2 E8672.939064 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X136.765462 Y64.470531 Z2 E8677.398572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032
G1 X136.308048 Y64.226038 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=end-early tail
G1 X134.878588 Y63.792416 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=end-early tail
G1 X133.392 Y63.646 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=end-early tail
G1 X131.905412 Y63.792416 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0032 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0032
G0 X131.905412 Y63.792416 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0033 note=intra-page lift
G0 X142.270866 Y73.469034 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0033 note=intra-page XY
G0 X142.270866 Y73.469034 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0033 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0033
G1 X141.253243 Y74.571052 Z2 E8677.741567 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X140.883 Y74.972 Z2 E8678.036555 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X140.135459 Y75.565111 Z2 E8678.770552 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X139.352941 Y76.185973 Z2 E8679.836308 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X138.991707 Y76.533263 Z2 E8680.485528 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X137.910382 Y77.572848 Z2 E8682.886494 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X137.285906 Y78.173219 Z2 E8684.585555 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X136.864188 Y78.646265 Z2 E8685.97345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X135.866012 Y79.765929 Z2 E8689.746397 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X134.867837 Y80.885592 Z2 E8694.205334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X134.85423 Y80.900855 Z2 E8694.270857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X133.956102 Y82.076627 Z2 E8699.350261 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X133.04556 Y83.268649 Z2 E8705.181178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X132.23025 Y84.336 Z2 E8710.984381 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X132.142537 Y84.466069 Z2 E8711.698086 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=prime ramp
G1 X130.9 Y86.308612 Z2 E8721.861512 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X129.586301 Y88.44577 Z2 E8733.334174 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X128.310693 Y90.743363 Z2 E8745.352486 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X127.094719 Y93.197281 Z2 E8757.877156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X125.95992 Y95.803415 Z2 E8770.876584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X124.92784 Y98.557652 Z2 E8784.327761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X124.020019 Y101.455884 Z2 E8798.217167 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X123.258 Y104.494 Z2 E8812.541664 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X126.296116 Y103.731981 Z2 E8826.86616 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X129.194348 Y102.82416 Z2 E8840.755567 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X131.948585 Y101.79208 Z2 E8854.206743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X134.554719 Y100.657281 Z2 E8867.206172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X137.008637 Y99.441307 Z2 E8879.730842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X139.30623 Y98.165699 Z2 E8891.749153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X141.443388 Y96.852 Z2 E8903.221815 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X143.416 Y95.52175 Z2 E8914.102698 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X146.851145 Y92.89777 Z2 E8933.871437 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X149.578781 Y90.466094 Z2 E8950.582995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X151.566027 Y88.399059 Z2 E8963.696224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X152.78 Y86.869 Z2 E8972.62852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X154.282966 Y85.481134 Z2 E8981.98427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X155.573525 Y84.153178 Z2 E8990.45286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X156.66167 Y82.883285 Z2 E8998.10087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X157.557391 Y81.669609 Z2 E9004.999271 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X158.27068 Y80.510302 Z2 E9011.224251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X158.811529 Y79.403518 Z2 E9016.8579 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X159.18993 Y78.347407 Z2 E9021.988438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X159.415875 Y77.340125 Z2 E9026.70948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X159.499355 Y76.379823 Z2 E9031.117762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X159.450361 Y75.464654 Z2 E9035.309067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X159.278886 Y74.592772 Z2 E9039.372804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X158.994922 Y73.762328 Z2 E9043.386541 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X158.608459 Y72.971476 Z2 E9047.412056 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X158.12949 Y72.218369 Z2 E9051.493764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X156.934 Y70.818 Z2 E9059.914331 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X155.533631 Y69.62251 Z2 E9068.334898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X154.780524 Y69.143541 Z2 E9072.416605 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X153.989672 Y68.757078 Z2 E9076.44212 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X153.159228 Y68.473114 Z2 E9080.455857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X152.287346 Y68.301639 Z2 E9084.519594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X151.372177 Y68.252645 Z2 E9088.710899 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X150.411875 Y68.336125 Z2 E9093.119181 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X149.404593 Y68.56207 Z2 E9097.840223 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X148.348482 Y68.940471 Z2 E9102.970762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X147.241698 Y69.48132 Z2 E9108.60441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X146.082391 Y70.194609 Z2 E9114.82939 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X146.056236 Y70.213912 Z2 E9114.978048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033
G1 X144.868715 Y71.09033 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=end-early tail
G1 X143.598822 Y72.178475 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=end-early tail
G1 X142.270866 Y73.469034 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0033 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0033
G0 X142.270866 Y73.469034 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0034 note=intra-page lift
G0 X155.361038 Y68.267048 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0034 note=intra-page XY
G0 X155.361038 Y68.267048 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0034 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0034
G1 X156.065202 Y69.584445 Z2 E9115.318205 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X156.069147 Y69.589252 Z2 E9115.321044 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X157.012846 Y70.739154 Z2 E9116.338677 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X157.022461 Y70.747044 Z2 E9116.350029 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X158.167555 Y71.686798 Z2 E9118.039462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X158.184008 Y71.695593 Z2 E9118.065005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X159.484952 Y72.390962 Z2 E9120.420561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X159.508756 Y72.398183 Z2 E9120.465971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X160.914412 Y72.824584 Z2 E9123.481974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X160.945356 Y72.827632 Z2 E9123.552927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X162.401 Y72.971 Z2 E9127.223701 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X162.438133 Y72.967343 Z2 E9127.325874 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X163.887588 Y72.824584 Z2 E9131.645743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X163.929245 Y72.811947 Z2 E9131.78481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X165.317048 Y72.390962 Z2 E9136.748098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X165.360924 Y72.36751 Z2 E9136.929738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X166.634445 Y71.686798 Z2 E9142.530767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X166.67771 Y71.651292 Z2 E9142.760655 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X167.789154 Y70.739154 Z2 E9148.993751 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X167.828605 Y70.691082 Z2 E9149.277563 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=prime ramp
G1 X168.736798 Y69.584445 Z2 E9155.824624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X169.440962 Y68.267048 Z2 E9162.656087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X169.874584 Y66.837588 Z2 E9169.487549 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X170.021 Y65.351 Z2 E9176.319012 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X169.874584 Y63.864412 Z2 E9183.150475 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X169.440962 Y62.434952 Z2 E9189.981937 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X168.736798 Y61.117555 Z2 E9196.8134 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X167.789154 Y59.962846 Z2 E9203.644863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X166.634445 Y59.015202 Z2 E9210.476325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X165.317048 Y58.311038 Z2 E9217.307788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X163.887588 Y57.877416 Z2 E9224.139251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X162.401 Y57.731 Z2 E9230.970713 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X160.914412 Y57.877416 Z2 E9237.802176 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X159.484952 Y58.311038 Z2 E9244.633639 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X158.167555 Y59.015202 Z2 E9251.465102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X157.012846 Y59.962846 Z2 E9258.296564 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X156.065202 Y61.117555 Z2 E9265.128027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X155.361038 Y62.434952 Z2 E9271.95949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X155.077974 Y63.368089 Z2 E9276.418998 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034
G1 X154.927416 Y63.864412 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=end-early tail
G1 X154.781 Y65.351 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=end-early tail
G1 X154.927416 Y66.837588 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=end-early tail
G1 X155.361038 Y68.267048 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0034 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0034
G0 X155.361038 Y68.267048 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0035 note=intra-page lift
G0 X157.608101 Y57.369617 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0035 note=intra-page XY
G0 X157.608101 Y57.369617 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0035 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0035
G1 X158.665907 Y57.526528 Z2 E9276.593327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X159.096008 Y57.547657 Z2 E9276.761993 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X159.734 Y57.579 Z2 E9277.116315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X160.594201 Y57.536741 Z2 E9277.790978 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X160.802093 Y57.526528 Z2 E9277.987961 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X161.859899 Y57.369617 Z2 E9279.208266 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X162.075708 Y57.31556 Z2 E9279.505954 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X162.897232 Y57.109779 Z2 E9280.777229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X163.51215 Y56.889758 Z2 E9281.90692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X163.904101 Y56.749515 Z2 E9282.694851 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X164.87081 Y56.292296 Z2 E9284.961131 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X164.883105 Y56.284927 Z2 E9284.993876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X165.788049 Y55.742524 Z2 E9287.57607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X166.145438 Y55.477466 Z2 E9288.766823 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X166.646984 Y55.105495 Z2 E9290.539668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X167.29574 Y54.517497 Z2 E9293.22576 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X167.439343 Y54.387343 Z2 E9293.851924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X168.157495 Y53.594984 Z2 E9297.512838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X168.298563 Y53.404776 Z2 E9298.370687 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X168.794524 Y52.736049 Z2 E9301.522411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X169.137652 Y52.163576 Z2 E9304.201604 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X169.344296 Y51.81881 Z2 E9305.880643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X169.801515 Y50.852101 Z2 E9310.587533 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X169.811173 Y50.82511 Z2 E9310.718512 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=prime ramp
G1 X170.161779 Y49.845232 Z2 E9315.477974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X170.421617 Y48.807899 Z2 E9320.36854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X170.578528 Y47.750093 Z2 E9325.259106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X170.631 Y46.682 Z2 E9330.149672 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X170.578528 Y45.613907 Z2 E9335.040238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X170.421617 Y44.556101 Z2 E9339.930804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X170.161779 Y43.518768 Z2 E9344.82137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X169.801515 Y42.511899 Z2 E9349.711936 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X169.344296 Y41.54519 Z2 E9354.602502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X168.794524 Y40.627951 Z2 E9359.493068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X168.157495 Y39.769016 Z2 E9364.383634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X167.439343 Y38.976657 Z2 E9369.2742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X166.646984 Y38.258505 Z2 E9374.164766 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X165.788049 Y37.621476 Z2 E9379.055332 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X164.87081 Y37.071704 Z2 E9383.945898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X163.904101 Y36.614485 Z2 E9388.836464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X162.897232 Y36.254221 Z2 E9393.72703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X161.859899 Y35.994383 Z2 E9398.617596 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X160.802093 Y35.837472 Z2 E9403.508162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X159.734 Y35.785 Z2 E9408.398728 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X158.665907 Y35.837472 Z2 E9413.289294 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X157.608101 Y35.994383 Z2 E9418.17986 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X156.570768 Y36.254221 Z2 E9423.070426 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X155.563899 Y36.614485 Z2 E9427.960993 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X154.59719 Y37.071704 Z2 E9432.851559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X153.679951 Y37.621476 Z2 E9437.742125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X152.821016 Y38.258505 Z2 E9442.632691 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X152.028657 Y38.976657 Z2 E9447.523257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X151.310505 Y39.769016 Z2 E9452.413823 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X151.145184 Y39.991925 Z2 E9453.683013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X150.673476 Y40.627951 Z2.395929 E9457.731834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=2 matz1=2.395929 note=collision lift
G1 X150.123704 Y41.54519 Z2.930619 E9463.199653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X149.666485 Y42.511899 Z3.46531 E9468.667472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X149.306221 Y43.518768 Z4 E9474.135291 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=3.46531 matz1=4 note=collision lift
G1 X149.046383 Y44.556101 Z4 E9479.025857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=4 matz1=4 note=collision lift
G1 X148.889472 Y45.613907 Z3.46531 E9484.493676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=4 matz1=3.46531 note=collision lift
G1 X148.837 Y46.682 Z2.930619 E9489.961495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X148.889472 Y47.750093 Z2.395929 E9495.429315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X149.005662 Y48.533379 Z2 E9499.478136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 matz0=2.395929 matz1=2 note=collision lift
G1 X149.046383 Y48.807899 Z2 E9500.747326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X149.306221 Y49.845232 Z2 E9505.637892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X149.666485 Y50.852101 Z2 E9510.528458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X150.123704 Y51.81881 Z2 E9515.419024 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X150.673476 Y52.736049 Z2 E9520.30959 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X151.310505 Y53.594984 Z2 E9525.200156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X152.028657 Y54.387343 Z2 E9530.090722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X152.821016 Y55.105495 Z2 E9534.981288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X153.099653 Y55.312146 Z2 E9536.567776 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035
G1 X153.679951 Y55.742524 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=end-early tail
G1 X154.59719 Y56.292296 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=end-early tail
G1 X155.563899 Y56.749515 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=end-early tail
G1 X156.570768 Y57.109779 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=end-early tail
G1 X157.608101 Y57.369617 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0035 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0035
G0 X157.608101 Y57.369617 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0036 note=intra-page lift
G0 X171.057836 Y63.730868 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0036 note=intra-page XY
G0 X171.057836 Y63.730868 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0036 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0036
G1 X171.002485 Y63.847899 Z2 E9536.57033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.642221 Y64.854768 Z2 E9536.786869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.569045 Y65.146902 Z2 E9536.910771 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.382383 Y65.892101 Z2 E9537.352065 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.275009 Y66.615959 Z2 E9537.939756 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.225472 Y66.949907 Z2 E9538.26592 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.173 Y68.018 Z2 E9539.528434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.177564 Y68.110904 Z2 E9539.654732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.225472 Y69.086093 Z2 E9541.139606 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.302305 Y69.604061 Z2 E9542.055698 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.382383 Y70.143899 Z2 E9543.099437 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.614248 Y71.069556 Z2 E9545.142654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X170.642221 Y71.181232 Z2 E9545.407926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X171.002485 Y72.188101 Z2 E9548.065074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X171.137375 Y72.473304 Z2 E9548.915601 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X171.459704 Y73.15481 Z2 E9551.07088 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X171.843282 Y73.794772 Z2 E9553.374538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X172.009476 Y74.072049 Z2 E9554.425345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X172.646505 Y74.930984 Z2 E9558.128468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X172.718597 Y75.010525 Z2 E9558.519465 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X173.364657 Y75.723343 Z2 E9562.18025 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X173.763266 Y76.084621 Z2 E9564.350382 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X174.157016 Y76.441495 Z2 E9566.580691 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X174.934994 Y77.018482 Z2 E9570.86729 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=prime ramp
G1 X175.015951 Y77.078524 Z2 E9571.328241 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X175.93319 Y77.628296 Z2 E9576.218807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X176.899899 Y78.085515 Z2 E9581.109373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X177.906768 Y78.445779 Z2 E9585.999939 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X178.944101 Y78.705617 Z2 E9590.890505 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X180.001907 Y78.862528 Z2 E9595.781071 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X181.07 Y78.915 Z2 E9600.671637 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X182.138093 Y78.862528 Z2 E9605.562203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X183.195899 Y78.705617 Z2 E9610.452769 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X184.233232 Y78.445779 Z2 E9615.343335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X185.240101 Y78.085515 Z2 E9620.233901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X186.20681 Y77.628296 Z2 E9625.124467 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X187.124049 Y77.078524 Z2 E9630.015033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X187.982984 Y76.441495 Z2 E9634.905599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X188.775343 Y75.723343 Z2 E9639.796165 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X189.493495 Y74.930984 Z2 E9644.686731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X190.130524 Y74.072049 Z2 E9649.577297 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X190.680296 Y73.15481 Z2 E9654.467863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.137515 Y72.188101 Z2 E9659.35843 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.497779 Y71.181232 Z2 E9664.248996 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.757617 Y70.143899 Z2 E9669.139562 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.914528 Y69.086093 Z2 E9674.030128 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.967 Y68.018 Z2 E9678.920694 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.914528 Y66.949907 Z2 E9683.81126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.757617 Y65.892101 Z2 E9688.701826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.497779 Y64.854768 Z2 E9693.592392 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X191.137515 Y63.847899 Z2 E9698.482958 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X190.680296 Y62.88119 Z2 E9703.373524 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X190.130524 Y61.963951 Z2 E9708.26409 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X189.493495 Y61.105016 Z2 E9713.154656 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X188.775343 Y60.312657 Z2 E9718.045222 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X187.982984 Y59.594505 Z2 E9722.935788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X187.124049 Y58.957476 Z2 E9727.826354 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X186.20681 Y58.407704 Z2 E9732.71692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X185.240101 Y57.950485 Z2 E9737.607486 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X184.233232 Y57.590221 Z2 E9742.498052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X183.195899 Y57.330383 Z2 E9747.388618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X182.138093 Y57.173472 Z2 E9752.279184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X181.07 Y57.121 Z2 E9757.16975 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X180.001907 Y57.173472 Z2 E9762.060316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X178.944101 Y57.330383 Z2 E9766.950882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X177.906768 Y57.590221 Z2 E9771.841448 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X176.899899 Y57.950485 Z2 E9776.732014 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X175.93319 Y58.407704 Z2 E9781.62258 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X175.015951 Y58.957476 Z2 E9786.513146 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X174.157016 Y59.594505 Z2 E9791.403712 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X173.995901 Y59.740532 Z2 E9792.398144 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036
G1 X173.364657 Y60.312657 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=end-early tail
G1 X172.646505 Y61.105016 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=end-early tail
G1 X172.009476 Y61.963951 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=end-early tail
G1 X171.459704 Y62.88119 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=end-early tail
G1 X171.057836 Y63.730868 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0036 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0036
G0 X171.057836 Y63.730868 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0037 note=intra-page lift
G0 X175.626517 Y56.108484 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0037 note=intra-page XY
G0 X175.626517 Y56.108484 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0037 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0037
G1 X175.93319 Y56.292296 Z2.286456 E9792.430141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2 matz1=2.286456 note=collision lift
G1 X176.668211 Y56.639935 Z2.937888 E9792.74114 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.286456 matz1=2.937888 note=collision lift
G1 X176.899899 Y56.749515 Z3.143228 E9792.90777 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.937888 matz1=3.143228 note=collision lift
G1 X177.760782 Y57.057544 Z3.875777 E9793.770125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.143228 matz1=3.875777 note=collision lift
G1 X177.906768 Y57.109779 Z4 E9793.957861 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.875777 matz1=4 note=collision lift
G1 X178.944101 Y57.369617 Z4 E9795.175079 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=4 matz1=4 note=collision lift
G1 X179.149312 Y57.400057 Z3.896272 E9795.485101 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=4 matz1=3.896272 note=collision lift
G1 X180.001907 Y57.526528 Z3.46531 E9796.948788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.896272 matz1=3.46531 note=collision lift
G1 X180.481046 Y57.550067 Z3.225451 E9797.886067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.46531 matz1=3.225451 note=collision lift
G1 X181.07 Y57.579 Z2.930619 E9799.15832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.225451 matz1=2.930619 note=collision lift
G1 X181.821071 Y57.542102 Z2.554631 E9800.973023 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.930619 matz1=2.554631 note=collision lift
G1 X182.138093 Y57.526528 Z2.395929 E9801.803675 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.554631 matz1=2.395929 note=collision lift
G1 X182.921379 Y57.410338 Z2 E9804.043356 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.395929 matz1=2 note=collision lift
G1 X183.178375 Y57.372217 Z2 E9804.74597 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X183.195899 Y57.369617 Z2 E9804.794628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X184.233232 Y57.109779 Z2 E9807.909073 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X184.621999 Y56.970676 Z2 E9809.204906 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X185.240101 Y56.749515 Z2 E9811.372177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X186.002637 Y56.388863 Z2 E9814.349834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X186.20681 Y56.292296 Z2 E9815.183938 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X187.124049 Y55.742524 Z2 E9819.344359 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X187.288514 Y55.620548 Z2 E9820.180751 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X187.982984 Y55.105495 Z2 E9823.853438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X188.453769 Y54.6788 Z2 E9826.697659 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 note=prime ramp
G1 X188.775343 Y54.387343 Z2 E9828.682462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X189.493495 Y53.594984 Z2 E9833.573028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X190.130524 Y52.736049 Z2 E9838.463594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X190.680296 Y51.81881 Z2 E9843.35416 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.137515 Y50.852101 Z2 E9848.244726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.497779 Y49.845232 Z2 E9853.135292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.757617 Y48.807899 Z2 E9858.025858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.914528 Y47.750093 Z2 E9862.916424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.967 Y46.682 Z2 E9867.80699 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.914528 Y45.613907 Z2 E9872.697556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.757617 Y44.556101 Z2 E9877.588122 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.497779 Y43.518768 Z2 E9882.478688 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X191.137515 Y42.511899 Z2 E9887.369254 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X190.680296 Y41.54519 Z2 E9892.25982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X190.130524 Y40.627951 Z2 E9897.150386 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X189.493495 Y39.769016 Z2 E9902.040952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X188.775343 Y38.976657 Z2 E9906.931518 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X187.982984 Y38.258505 Z2 E9911.822084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X187.124049 Y37.621476 Z2 E9916.71265 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X186.20681 Y37.071704 Z2 E9921.603216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X185.240101 Y36.614485 Z2 E9926.493782 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X184.233232 Y36.254221 Z2 E9931.384348 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X183.195899 Y35.994383 Z2 E9936.274914 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X182.138093 Y35.837472 Z2 E9941.16548 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X181.07 Y35.785 Z2 E9946.056046 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X180.001907 Y35.837472 Z2 E9950.946612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X178.944101 Y35.994383 Z2 E9955.837178 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X177.906768 Y36.254221 Z2 E9960.727745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X176.899899 Y36.614485 Z2 E9965.618311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X175.93319 Y37.071704 Z2 E9970.508877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X175.015951 Y37.621476 Z2 E9975.399443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X174.157016 Y38.258505 Z2 E9980.290009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X173.364657 Y38.976657 Z2 E9985.180575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X172.646505 Y39.769016 Z2 E9990.071141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X172.481184 Y39.991925 Z2 E9991.340331 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X172.009476 Y40.627951 Z2.395929 E9995.389152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2 matz1=2.395929 note=collision lift
G1 X171.459704 Y41.54519 Z2.930619 E10000.856971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X171.002485 Y42.511899 Z3.46531 E10006.32479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X170.642221 Y43.518768 Z4 E10011.792609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.46531 matz1=4 note=collision lift
G1 X170.382383 Y44.556101 Z4 E10016.683175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=4 matz1=4 note=collision lift
G1 X170.225472 Y45.613907 Z3.46531 E10022.150994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=4 matz1=3.46531 note=collision lift
G1 X170.173 Y46.682 Z2.930619 E10027.618813 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X170.225472 Y47.750093 Z2.395929 E10033.086633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X170.341662 Y48.533379 Z2 E10037.135454 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.395929 matz1=2 note=collision lift
G1 X170.382383 Y48.807899 Z2 E10038.404644 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X170.642221 Y49.845232 Z2 E10043.29521 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X171.002485 Y50.852101 Z2 E10048.185776 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X171.459704 Y51.81881 Z2 E10053.076342 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X171.87462 Y52.511056 Z2 E10056.767283 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037
G1 X172.009476 Y52.736049 Z2.131156 E10058.108505 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2 matz1=2.131156 note=collision lift
G1 X172.317588 Y53.151491 Z2.38977 E10060.75313 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.131156 matz1=2.38977 note=collision lift
G1 X172.646505 Y53.594984 Z2.665847 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.38977 matz1=2.665847 note=collision lift
G1 X173.364657 Y54.387343 Z3.200537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=2.665847 matz1=3.200537 note=collision lift
G1 X174.157016 Y55.105495 Z3.735228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.200537 matz1=3.735228 note=collision lift
G1 X174.58251 Y55.421062 Z4.000099 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.735228 matz1=4 note=collision lift
G1 X175.015951 Y55.742524 Z3.73028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=4 matz1=3.73028 note=collision lift
G1 X175.626517 Y56.108484 Z3.37436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0037 matz0=3.73028 matz1=3.37436 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0037
G0 X175.626517 Y56.108484 Z7.37436 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0038 note=intra-page lift
G0 X178.972051 Y78.662237 Z7.37436 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0038 note=intra-page XY
G0 X178.972051 Y78.662237 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0038 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0038
G1 X178.944101 Y78.666383 Z2 E10060.753252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X177.906768 Y78.926221 Z2 E10060.936793 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X177.527925 Y79.061773 Z2 E10061.096125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X176.899899 Y79.286485 Z2 E10061.468994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X176.146891 Y79.642631 Z2 E10062.125111 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X175.93319 Y79.743704 Z2 E10062.349852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X175.015951 Y80.293476 Z2 E10063.57937 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X174.859952 Y80.409173 Z2 E10063.840086 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X174.157016 Y80.930505 Z2 E10065.157546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X173.694041 Y81.350122 Z2 E10066.241052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X173.364657 Y81.648657 Z2 E10067.08438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X172.655855 Y82.430701 Z2 E10069.328009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X172.646505 Y82.441016 Z2 E10069.359873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X172.009476 Y83.299951 Z2 E10071.984024 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X171.795251 Y83.657364 Z2 E10073.100955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X171.459704 Y84.21719 Z2 E10074.956834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X171.09743 Y84.983155 Z2 E10077.559892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X171.002485 Y85.183899 Z2 E10078.278302 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X170.642221 Y86.190768 Z2 E10081.948429 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X170.591547 Y86.393072 Z2 E10082.704819 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X170.382383 Y87.228101 Z2 E10085.967215 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X170.288597 Y87.860356 Z2 E10088.535737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X170.225472 Y88.285907 Z2 E10090.334659 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X170.173 Y89.354 Z2 E10095.050761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X170.17302 Y89.354411 Z2 E10095.052644 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=prime ramp
G1 X170.225472 Y90.422093 Z2 E10099.941327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X170.382383 Y91.479899 Z2 E10104.831893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X170.642221 Y92.517232 Z2 E10109.722459 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X171.002485 Y93.524101 Z2 E10114.613026 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X171.459704 Y94.49081 Z2 E10119.503592 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X172.009476 Y95.408049 Z2 E10124.394158 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X172.646505 Y96.266984 Z2 E10129.284724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X173.364657 Y97.059343 Z2 E10134.17529 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X174.157016 Y97.777495 Z2 E10139.065856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X175.015951 Y98.414524 Z2 E10143.956422 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X175.93319 Y98.964296 Z2 E10148.846988 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X176.899899 Y99.421515 Z2 E10153.737554 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X177.906768 Y99.781779 Z2 E10158.62812 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X178.944101 Y100.041617 Z2 E10163.518686 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X180.001907 Y100.198528 Z2 E10168.409252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X181.07 Y100.251 Z2 E10173.299818 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X182.138093 Y100.198528 Z2 E10178.190384 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X183.195899 Y100.041617 Z2 E10183.08095 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X184.233232 Y99.781779 Z2 E10187.971516 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X185.240101 Y99.421515 Z2 E10192.862082 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X186.20681 Y98.964296 Z2 E10197.752648 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X187.124049 Y98.414524 Z2 E10202.643214 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X187.982984 Y97.777495 Z2 E10207.53378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X188.775343 Y97.059343 Z2 E10212.424346 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X189.493495 Y96.266984 Z2 E10217.314912 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X190.130524 Y95.408049 Z2 E10222.205478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X190.680296 Y94.49081 Z2 E10227.096044 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.137515 Y93.524101 Z2 E10231.98661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.497779 Y92.517232 Z2 E10236.877176 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.757617 Y91.479899 Z2 E10241.767742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.914528 Y90.422093 Z2 E10246.658308 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.967 Y89.354 Z2 E10251.548874 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.914528 Y88.285907 Z2 E10256.43944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.757617 Y87.228101 Z2 E10261.330006 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.497779 Y86.190768 Z2 E10266.220572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X191.137515 Y85.183899 Z2 E10271.111139 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X190.680296 Y84.21719 Z2 E10276.001705 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X190.130524 Y83.299951 Z2 E10280.892271 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X189.493495 Y82.441016 Z2 E10285.782837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X188.775343 Y81.648657 Z2 E10290.673403 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X187.982984 Y80.930505 Z2 E10295.563969 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X187.760075 Y80.765184 Z2 E10296.833159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038
G1 X187.124049 Y80.293476 Z2.395929 E10300.88198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=2 matz1=2.395929 note=collision lift
G1 X186.20681 Y79.743704 Z2.930619 E10306.349799 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X185.240101 Y79.286485 Z3.46531 E10311.817618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X184.233232 Y78.926221 Z4 E10317.285437 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=3.46531 matz1=4 note=collision lift
G1 X183.466146 Y78.734076 Z4 E10320.901908 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=4 matz1=4 note=collision lift
G1 X183.195899 Y78.666383 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=4 matz1=4 note=collision lift
G1 X182.138093 Y78.509472 Z3.46531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=4 matz1=3.46531 note=collision lift
G1 X181.07 Y78.457 Z2.930619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X180.001907 Y78.509472 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X179.218621 Y78.625662 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 matz0=2.395929 matz1=2 note=collision lift
G1 X178.972051 Y78.662237 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0038 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0038
G0 X178.972051 Y78.662237 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0039 note=intra-page lift
G0 X162.821798 Y90.126555 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0039 note=intra-page XY
G0 X162.821798 Y90.126555 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0039 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0039
G1 X161.874154 Y88.971846 Z2 E10321.242065 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X161.869346 Y88.967901 Z2 E10321.244903 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X160.719445 Y88.024202 Z2 E10322.262536 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X160.708476 Y88.018339 Z2 E10322.273889 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X159.402048 Y87.320038 Z2 E10323.963321 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X159.384195 Y87.314622 Z2 E10323.988864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X157.972588 Y86.886416 Z2 E10326.34442 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X157.947833 Y86.883978 Z2 E10326.38983 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X156.486 Y86.74 Z2 E10329.405834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X156.455056 Y86.743048 Z2 E10329.476787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X154.999412 Y86.886416 Z2 E10333.147561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X154.963706 Y86.897247 Z2 E10333.249733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X153.569952 Y87.320038 Z2 E10337.569602 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X153.531561 Y87.340559 Z2 E10337.70867 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X152.252555 Y88.024202 Z2 E10342.671957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X152.214097 Y88.055763 Z2 E10342.853597 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X151.097846 Y88.971846 Z2 E10348.454627 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X151.06234 Y89.015111 Z2 E10348.684515 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X150.150202 Y90.126555 Z2 E10354.91761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X150.120886 Y90.1814 Z2 E10355.201422 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=prime ramp
G1 X149.446038 Y91.443952 Z2 E10361.748483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X149.012416 Y92.873412 Z2 E10368.579946 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X148.866 Y94.36 Z2 E10375.411409 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X149.012416 Y95.846588 Z2 E10382.242871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X149.446038 Y97.276048 Z2 E10389.074334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X150.150202 Y98.593445 Z2 E10395.905797 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X151.097846 Y99.748154 Z2 E10402.73726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X152.252555 Y100.695798 Z2 E10409.568722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X153.569952 Y101.399962 Z2 E10416.400185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X154.999412 Y101.833584 Z2 E10423.231648 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X156.486 Y101.98 Z2 E10430.06311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X157.972588 Y101.833584 Z2 E10436.894573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X159.402048 Y101.399962 Z2 E10443.726036 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X160.719445 Y100.695798 Z2 E10450.557498 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X161.874154 Y99.748154 Z2 E10457.388961 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X162.821798 Y98.593445 Z2 E10464.220424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X163.525962 Y97.276048 Z2 E10471.051887 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X163.959584 Y95.846588 Z2 E10477.883349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X164.055163 Y94.876159 Z2 E10482.342857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039
G1 X164.106 Y94.36 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=end-early tail
G1 X163.959584 Y92.873412 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=end-early tail
G1 X163.525962 Y91.443952 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=end-early tail
G1 X162.821798 Y90.126555 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0039 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0039
G0 X162.821798 Y90.126555 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0040 note=intra-page lift
G0 X161.807268 Y102.341804 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0040 note=intra-page XY
G0 X161.807268 Y102.341804 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0040 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0040
G1 X160.377092 Y102.223021 Z2 E10482.656814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X160.312199 Y102.222023 Z2 E10482.685852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X158.812377 Y102.198952 Z2 E10483.714838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X158.658885 Y102.196591 Z2 E10483.858839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X157.313633 Y102.254325 Z2 E10485.429813 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X156.762 Y102.278 Z2 E10486.233814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X155.821378 Y102.161099 Z2 E10487.830779 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X154.96157 Y102.054242 Z2 E10489.530168 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X154.328135 Y102.040776 Z2 E10490.917736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X152.828474 Y102.008894 Z2 E10494.690682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X152.301313 Y101.997688 Z2 E10496.179903 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X151.330446 Y102.057689 Z2 E10499.149619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X149.833302 Y102.150216 Z2 E10504.294546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X148.915898 Y102.206914 Z2 E10507.786167 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X148.341004 Y102.289852 Z2 E10510.125464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X146.856374 Y102.504033 Z2 E10516.642371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=prime ramp
G1 X144.94 Y102.7805 Z2 E10525.497197 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X142.772704 Y103.234733 Z2 E10535.624173 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X140.508289 Y103.817023 Z2 E10546.316859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X138.163589 Y104.539692 Z2 E10557.537567 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X135.755438 Y105.415063 Z2 E10569.255729 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X133.300669 Y106.455456 Z2 E10581.448707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X130.816117 Y107.673195 Z2 E10594.102608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X128.318616 Y109.080603 Z2 E10607.213066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X125.825 Y110.69 Z2 E10620.785956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X128.318616 Y112.299397 Z2 E10634.358845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X130.816117 Y113.706805 Z2 E10647.469303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X133.300669 Y114.924544 Z2 E10660.123205 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X135.755438 Y115.964938 Z2 E10672.316183 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X138.163589 Y116.840308 Z2 E10684.034345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X140.508289 Y117.562977 Z2 E10695.255052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X142.772704 Y118.145267 Z2 E10705.947739 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X144.94 Y118.5995 Z2 E10716.074715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X148.915898 Y119.173086 Z2 E10734.445808 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X152.301313 Y119.382313 Z2 E10749.957755 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X154.96157 Y119.325758 Z2 E10762.126577 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X156.762 Y119.102 Z2 E10770.42377 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X158.658885 Y119.183409 Z2 E10779.106718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X160.377092 Y119.156979 Z2 E10786.965471 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X161.92439 Y119.028469 Z2 E10794.066045 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X163.308547 Y118.803641 Z2 E10800.479128 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X164.537331 Y118.488256 Z2 E10806.280833 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X165.61851 Y118.088076 Z2 E10811.553183 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X166.559852 Y117.608862 Z2 E10816.383929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X167.369125 Y117.056375 Z2 E10820.865184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X168.054097 Y116.436376 Z2 E10825.090413 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X168.622537 Y115.754627 Z2 E10829.149832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X169.082212 Y115.016888 Z2 E10833.12505 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X169.440891 Y114.228922 Z2 E10837.084406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X169.706341 Y113.396489 Z2 E10841.080221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X169.88633 Y112.52535 Z2 E10845.148321 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X170.021 Y110.69 Z2 E10853.564432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X169.88633 Y108.85465 Z2 E10861.980544 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X169.706341 Y107.983511 Z2 E10866.048644 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X169.440891 Y107.151078 Z2 E10870.044458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X169.082212 Y106.363112 Z2 E10874.003815 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X168.622537 Y105.625373 Z2 E10877.979033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X168.054097 Y104.943624 Z2 E10882.038451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X167.369125 Y104.323625 Z2 E10886.263681 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X166.561835 Y103.772492 Z2 E10890.733953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040
G1 X166.559852 Y103.771138 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=end-early tail
G1 X165.61851 Y103.291924 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=end-early tail
G1 X164.537331 Y102.891744 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=end-early tail
G1 X163.308547 Y102.576359 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=end-early tail
G1 X161.92439 Y102.351531 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=end-early tail
G1 X161.807268 Y102.341804 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0040 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0040
G0 X161.807268 Y102.341804 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0041 note=intra-page lift
G0 X171.002485 Y106.519899 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0041 note=intra-page XY
G0 X171.002485 Y106.519899 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0041 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0041
G1 X170.642221 Y107.526768 Z2 E10890.908282 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.537589 Y107.944482 Z2 E10891.076948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.382383 Y108.564101 Z2 E10891.43127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.256013 Y109.416017 Z2 E10892.105934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.225472 Y109.621907 Z2 E10892.302917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.173 Y110.69 Z2 E10893.523221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.183916 Y110.912208 Z2 E10893.82091 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.225472 Y111.758093 Z2 E10895.092185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.321301 Y112.40412 Z2 E10896.221876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.382383 Y112.815899 Z2 E10897.009807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.642221 Y113.853232 Z2 E10899.276087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X170.64705 Y113.866728 Z2 E10899.308832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X171.002485 Y114.860101 Z2 E10901.891026 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X171.192727 Y115.262334 Z2 E10903.081778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X171.459704 Y115.82681 Z2 E10904.854623 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X171.909838 Y116.577813 Z2 E10907.540715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X172.009476 Y116.744049 Z2 E10908.166879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X172.646505 Y117.602984 Z2 E10911.827794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X172.805537 Y117.778448 Z2 E10912.685642 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X173.364657 Y118.395343 Z2 E10915.837367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X173.85919 Y118.843561 Z2 E10918.51656 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X174.157016 Y119.113495 Z2 E10920.195599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X175.015951 Y119.750524 Z2 E10924.902489 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X175.04054 Y119.765262 Z2 E10925.033467 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=prime ramp
G1 X175.93319 Y120.300296 Z2 E10929.792929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X176.899899 Y120.757515 Z2 E10934.683495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X177.906768 Y121.117779 Z2 E10939.574061 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X178.944101 Y121.377617 Z2 E10944.464628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X180.001907 Y121.534528 Z2 E10949.355194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X181.07 Y121.587 Z2 E10954.24576 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X182.138093 Y121.534528 Z2 E10959.136326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X183.195899 Y121.377617 Z2 E10964.026892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X184.233232 Y121.117779 Z2 E10968.917458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X185.240101 Y120.757515 Z2 E10973.808024 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X186.20681 Y120.300296 Z2 E10978.69859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X187.124049 Y119.750524 Z2 E10983.589156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X187.982984 Y119.113495 Z2 E10988.479722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X188.775343 Y118.395343 Z2 E10993.370288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X189.493495 Y117.602984 Z2 E10998.260854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X190.130524 Y116.744049 Z2 E11003.15142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X190.680296 Y115.82681 Z2 E11008.041986 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.137515 Y114.860101 Z2 E11012.932552 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.497779 Y113.853232 Z2 E11017.823118 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.757617 Y112.815899 Z2 E11022.713684 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.914528 Y111.758093 Z2 E11027.60425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.967 Y110.69 Z2 E11032.494816 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.914528 Y109.621907 Z2 E11037.385382 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.757617 Y108.564101 Z2 E11042.275948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.497779 Y107.526768 Z2 E11047.166514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X191.137515 Y106.519899 Z2 E11052.05708 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X190.680296 Y105.55319 Z2 E11056.947646 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X190.130524 Y104.635951 Z2 E11061.838212 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X189.493495 Y103.777016 Z2 E11066.728778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X188.775343 Y102.984657 Z2 E11071.619344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X187.982984 Y102.266505 Z2 E11076.50991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X187.760075 Y102.101184 Z2 E11077.7791 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X187.124049 Y101.629476 Z2.395929 E11081.827922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=2 matz1=2.395929 note=collision lift
G1 X186.20681 Y101.079704 Z2.930619 E11087.295741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X185.240101 Y100.622485 Z3.46531 E11092.76356 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X184.233232 Y100.262221 Z4 E11098.231379 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=3.46531 matz1=4 note=collision lift
G1 X183.195899 Y100.002383 Z4 E11103.121945 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=4 matz1=4 note=collision lift
G1 X182.138093 Y99.845472 Z3.46531 E11108.589764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=4 matz1=3.46531 note=collision lift
G1 X181.07 Y99.793 Z2.930619 E11114.057583 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X180.001907 Y99.845472 Z2.395929 E11119.525402 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X179.218621 Y99.961662 Z2 E11123.574224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 matz0=2.395929 matz1=2 note=collision lift
G1 X178.944101 Y100.002383 Z2 E11124.843414 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X177.906768 Y100.262221 Z2 E11129.73398 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X176.899899 Y100.622485 Z2 E11134.624546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X175.93319 Y101.079704 Z2 E11139.515112 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X175.015951 Y101.629476 Z2 E11144.405678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X174.157016 Y102.266505 Z2 E11149.296244 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X173.899977 Y102.499472 Z2 E11150.882731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041
G1 X173.364657 Y102.984657 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=end-early tail
G1 X172.646505 Y103.777016 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=end-early tail
G1 X172.009476 Y104.635951 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=end-early tail
G1 X171.459704 Y105.55319 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=end-early tail
G1 X171.002485 Y106.519899 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0041 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0041
G0 X171.002485 Y106.519899 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0042 note=intra-page lift
G0 X176.899899 Y121.958485 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0042 note=intra-page XY
G0 X176.899899 Y121.958485 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0042 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0042
G1 X175.93319 Y122.415704 Z2 E11151.05706 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X175.563835 Y122.637086 Z2 E11151.225726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X175.015951 Y122.965476 Z2 E11151.580048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X174.324198 Y123.478515 Z2 E11152.254712 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X174.157016 Y123.602505 Z2 E11152.451695 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X173.364657 Y124.320657 Z2 E11153.671999 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X173.215251 Y124.485502 Z2 E11153.969687 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X172.646505 Y125.113016 Z2 E11155.240963 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X172.257457 Y125.637588 Z2 E11156.370653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X172.009476 Y125.971951 Z2 E11157.158585 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X171.459704 Y126.88919 Z2 E11159.424865 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X171.453576 Y126.902147 Z2 E11159.45761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X171.002485 Y127.855899 Z2 E11162.039804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.852585 Y128.274841 Z2 E11163.230556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.642221 Y128.862768 Z2 E11165.003401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.429475 Y129.7121 Z2 E11167.689493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.382383 Y129.900101 Z2 E11168.315657 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.225472 Y130.957907 Z2 E11171.976572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.213852 Y131.194432 Z2 E11172.83442 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.173 Y132.026 Z2 E11175.986145 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.205749 Y132.692625 Z2 E11178.665338 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.225472 Y133.094093 Z2 E11180.344377 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.382383 Y134.151899 Z2 E11185.051267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.389348 Y134.179708 Z2 E11185.182245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=prime ramp
G1 X170.642221 Y135.189232 Z2 E11189.941707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X171.002485 Y136.196101 Z2 E11194.832273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X171.459704 Y137.16281 Z2 E11199.722839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X172.009476 Y138.080049 Z2 E11204.613406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X172.646505 Y138.938984 Z2 E11209.503972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X173.364657 Y139.731343 Z2 E11214.394538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X174.157016 Y140.449495 Z2 E11219.285104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X174.379925 Y140.614816 Z2 E11220.554293 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X175.015951 Y141.086524 Z2.395929 E11224.603115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2 matz1=2.395929 note=collision lift
G1 X175.93319 Y141.636296 Z2.930619 E11230.070934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X176.899899 Y142.093515 Z3.46531 E11235.538753 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X177.906768 Y142.453779 Z4 E11241.006572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=3.46531 matz1=4 note=collision lift
G1 X178.944101 Y142.713617 Z4 E11245.897138 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=4 matz1=4 note=collision lift
G1 X180.001907 Y142.870528 Z3.46531 E11251.364957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=4 matz1=3.46531 note=collision lift
G1 X181.07 Y142.923 Z2.930619 E11256.832776 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=3.46531 matz1=2.930619 note=collision lift
G1 X182.138093 Y142.870528 Z2.395929 E11262.300595 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X182.921379 Y142.754338 Z2 E11266.349417 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2.395929 matz1=2 note=collision lift
G1 X183.195899 Y142.713617 Z2 E11267.618607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X184.233232 Y142.453779 Z2 E11272.509173 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X185.240101 Y142.093515 Z2 E11277.399739 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X186.20681 Y141.636296 Z2 E11282.290305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X187.124049 Y141.086524 Z2 E11287.180871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X187.982984 Y140.449495 Z2 E11292.071437 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X188.775343 Y139.731343 Z2 E11296.962003 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X189.493495 Y138.938984 Z2 E11301.852569 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X190.130524 Y138.080049 Z2 E11306.743135 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X190.680296 Y137.16281 Z2 E11311.633701 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.137515 Y136.196101 Z2 E11316.524267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.497779 Y135.189232 Z2 E11321.414833 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.757617 Y134.151899 Z2 E11326.305399 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.914528 Y133.094093 Z2 E11331.195965 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.967 Y132.026 Z2 E11336.086531 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.914528 Y130.957907 Z2 E11340.977097 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.757617 Y129.900101 Z2 E11345.867663 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.497779 Y128.862768 Z2 E11350.758229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X191.137515 Y127.855899 Z2 E11355.648796 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X190.680296 Y126.88919 Z2 E11360.539362 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X190.130524 Y125.971951 Z2 E11365.429928 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X189.493495 Y125.113016 Z2 E11370.320494 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X188.775343 Y124.320657 Z2 E11375.21106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X187.982984 Y123.602505 Z2 E11380.101626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X187.760075 Y123.437184 Z2 E11381.370816 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042
G1 X187.124049 Y122.965476 Z2.395929 E11385.419637 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2 matz1=2.395929 note=collision lift
G1 X186.20681 Y122.415704 Z2.930619 E11390.887456 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2.395929 matz1=2.930619 note=collision lift
G1 X185.240101 Y121.958485 Z3.46531 E11396.355275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2.930619 matz1=3.46531 note=collision lift
G1 X184.233232 Y121.598221 Z4 E11401.823094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=3.46531 matz1=4 note=collision lift
G1 X183.195899 Y121.338383 Z4 E11406.71366 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=4 matz1=4 note=collision lift
G1 X182.138093 Y121.181472 Z3.46531 E11412.181479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=4 matz1=3.46531 note=collision lift
G1 X181.519165 Y121.151066 Z3.155472 E11415.349918 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=3.46531 matz1=3.155472 note=collision lift
G1 X181.07 Y121.129 Z2.930619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=3.155472 matz1=2.930619 note=collision lift
G1 X180.001907 Y121.181472 Z2.395929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2.930619 matz1=2.395929 note=collision lift
G1 X179.218621 Y121.297662 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 matz0=2.395929 matz1=2 note=collision lift
G1 X178.944101 Y121.338383 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=end-early tail
G1 X177.906768 Y121.598221 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=end-early tail
G1 X176.899899 Y121.958485 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0042 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0042
G0 X176.899899 Y121.958485 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0043 note=intra-page lift
G0 X163.959584 Y125.533412 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0043 note=intra-page XY
G0 X163.959584 Y125.533412 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0043 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0043
G1 X163.525962 Y124.103952 Z2 E11415.690075 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X163.523031 Y124.098468 Z2 E11415.692913 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X162.821798 Y122.786555 Z2 E11416.710546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X162.813908 Y122.77694 Z2 E11416.721899 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X161.874154 Y121.631846 Z2 E11418.411331 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X161.859732 Y121.620011 Z2 E11418.436875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X160.719445 Y120.684202 Z2 E11420.792431 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X160.697507 Y120.672476 Z2 E11420.837841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X159.402048 Y119.980038 Z2 E11423.853844 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X159.372293 Y119.971012 Z2 E11423.924797 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X157.972588 Y119.546416 Z2 E11427.595571 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X157.935455 Y119.542759 Z2 E11427.697743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X156.486 Y119.4 Z2 E11432.017612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X156.442678 Y119.404267 Z2 E11432.15668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X154.999412 Y119.546416 Z2 E11437.119968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X154.951804 Y119.560858 Z2 E11437.301607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X153.569952 Y119.980038 Z2 E11442.902637 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X153.520592 Y120.006422 Z2 E11443.132525 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X152.252555 Y120.684202 Z2 E11449.36562 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X152.204483 Y120.723653 Z2 E11449.649433 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=prime ramp
G1 X151.097846 Y121.631846 Z2 E11456.196494 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X150.150202 Y122.786555 Z2 E11463.027956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X149.446038 Y124.103952 Z2 E11469.859419 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X149.012416 Y125.533412 Z2 E11476.690882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X148.866 Y127.02 Z2 E11483.522344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X149.012416 Y128.506588 Z2 E11490.353807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X149.446038 Y129.936048 Z2 E11497.18527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X150.150202 Y131.253445 Z2 E11504.016732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X151.097846 Y132.408154 Z2 E11510.848195 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X152.252555 Y133.355798 Z2 E11517.679658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X153.569952 Y134.059962 Z2 E11524.511121 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X154.999412 Y134.493584 Z2 E11531.342583 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X156.486 Y134.64 Z2 E11538.174046 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X157.972588 Y134.493584 Z2 E11545.005509 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X159.402048 Y134.059962 Z2 E11551.836971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X160.719445 Y133.355798 Z2 E11558.668434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X161.874154 Y132.408154 Z2 E11565.499897 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X162.821798 Y131.253445 Z2 E11572.331359 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X163.281469 Y130.393462 Z2 E11576.790867 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043
G1 X163.525962 Y129.936048 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=end-early tail
G1 X163.959584 Y128.506588 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=end-early tail
G1 X164.106 Y127.02 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=end-early tail
G1 X163.959584 Y125.533412 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0043 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0043
G0 X163.959584 Y125.533412 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0044 note=intra-page lift
G0 X117.062 Y114.5 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0044 note=intra-page XY
G0 X117.062 Y114.5 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0044 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0044
G1 X117.71 Y114.522 Z2 E11576.854952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X118.365 Y114.432 Z2 E11577.052285 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X118.544038 Y114.366998 Z2 E11577.133863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X119.318 Y114.086 Z2 E11577.613775 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X119.890827 Y113.72591 Z2 E11578.162848 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X119.905 Y113.717 Z2 E11578.178203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X120.431 Y113.247 Z2 E11578.902843 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X120.88822 Y112.617692 Z2 E11579.877824 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X121.066 Y112.373 Z2 E11580.306733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X121.365 Y111.699 Z2 E11581.469228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X121.477914 Y111.252868 Z2 E11582.27879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X121.549 Y110.972 Z2 E11582.82158 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X121.59 Y109.826 Z2 E11585.221062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X121.576324 Y109.763946 Z2 E11585.365746 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X121.337 Y108.678 Z2 E11588.096998 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X121.160652 Y108.332397 Z2 E11589.138693 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X120.79 Y107.606 Z2 E11591.477765 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X120.336311 Y107.093448 Z2 E11593.597629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X119.973 Y106.683 Z2 E11595.398199 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X119.183338 Y106.151526 Z2 E11598.742557 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X118.927 Y105.979 Z2 E11599.887585 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X117.804128 Y105.581932 Z2 E11604.573474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X117.711 Y105.549 Z2 E11604.981529 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X116.842 Y105.437 Z2 E11608.731285 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X116.318745 Y105.480179 Z2 E11611.090382 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=prime ramp
G1 X115.509 Y105.547 Z2 E11614.806151 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X114.22 Y105.997 Z2 E11621.049996 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X113.06 Y106.771 Z2 E11627.427494 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X112.4 Y107.45 Z2 E11631.757973 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X111.856 Y108.24 Z2 E11636.144584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X111.447 Y109.122 Z2 E11640.590792 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X111.12 Y110.566 Z2 E11647.361801 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X111.107 Y111.569 Z2 E11651.949175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X111.264 Y112.574 Z2 E11656.601055 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X111.818 Y114.018 Z2 E11663.674191 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X112.39 Y114.896 Z2 E11668.466461 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X113.11 Y115.676 Z2 E11673.321024 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X114.428 Y116.607 Z2 E11680.700705 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X115.963 Y117.189 Z2 E11688.20832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X117.623 Y117.372 Z2 E11695.845937 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X119.305 Y117.131 Z2 E11703.616733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X120.899 Y116.466 Z2 E11711.515473 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X122.3 Y115.406 Z2 E11719.549862 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X123.078 Y114.508 Z2 E11724.983567 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X123.41 Y114.008 Z2 E11727.728382 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X123.947 Y112.927 Z2 E11733.248471 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X124.147 Y112.352 Z2 E11736.03263 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X124.401 Y111.152 Z2 E11741.642142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X124.452 Y110.535 Z2 E11744.473472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X124.451 Y109.913 Z2 E11747.318049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X124.291 Y108.672 Z2 E11753.04045 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X124.133 Y108.06 Z2 E11755.93106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X123.661 Y106.88 Z2 E11761.743222 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X122.992 Y105.784 Z2 E11767.615514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X122.588 Y105.279 Z2 E11770.573118 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X121.653 Y104.371 Z2 E11776.533631 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X120.569 Y103.626 Z2 E11782.548968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X119.979 Y103.322 Z2 E11785.584309 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X118.726 Y102.864 Z2 E11791.685421 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X118.07 Y102.714 Z2 E11794.762915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X116.881684 Y102.597637 Z2 E11800.223397 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044
G1 X116.722 Y102.582 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=end-early tail
G1 X115.359 Y102.678 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=end-early tail
G1 X114.018 Y103.003 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=end-early tail
G1 X113.369 Y103.25 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=end-early tail
G1 X112.135 Y103.909 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0044 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0044
; CLAYLINE_MARKER page=0 layer=1 text=layer 1 page_id=page-2-petal-flower-1 page_name=petal-flower z_mode=calibrated
G0 X112.135 Y103.909 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0044 note=vertical layer transition
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0044
G1 X113.369 Y103.25 Z4 E11800.494611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X113.46345 Y103.214054 Z4 E11800.535211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X114.018 Y103.003 Z4 E11800.830691 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X114.899137 Y102.789451 Z4 E11801.470652 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X115.359 Y102.678 Z4 E11801.895128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X116.383287 Y102.605857 Z4 E11803.029721 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X116.722 Y102.582 Z4 E11803.469208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X117.876924 Y102.695093 Z4 E11805.212418 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X118.07 Y102.714 Z4 E11805.540256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X118.726 Y102.864 Z4 E11806.758285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X119.320593 Y103.081337 Z4 E11808.018742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X119.979 Y103.322 Z4 E11809.544079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X120.569 Y103.626 Z4 E11811.113786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X120.680484 Y103.702619 Z4 E11811.448693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X121.653 Y104.371 Z4 E11814.585324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X121.882528 Y104.5939 Z4 E11815.502272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X122.588 Y105.279 Z4 E11818.498209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X122.910724 Y105.682405 Z4 E11820.179478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X122.992 Y105.784 Z4 E11820.614554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X123.661 Y106.88 Z4 E11825.160109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X123.692883 Y106.959708 Z4 E11825.480312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X124.133 Y108.06 Z4 E11830.109113 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X124.211729 Y108.364951 Z4 E11831.404774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=prime ramp
G1 X124.291 Y108.672 Z4 E11832.723193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X124.451 Y109.913 Z4 E11837.925377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X124.452 Y110.535 Z4 E11840.511356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X124.401 Y111.152 Z4 E11843.085292 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X124.147 Y112.352 Z4 E11848.184848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X123.947 Y112.927 Z4 E11850.715902 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X123.41 Y114.008 Z4 E11855.734165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X123.078 Y114.508 Z4 E11858.229451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X122.3 Y115.406 Z4 E11863.169183 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X120.899 Y116.466 Z4 E11870.473173 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X119.305 Y117.131 Z4 E11877.653845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X117.623 Y117.372 Z4 E11884.718205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X115.963 Y117.189 Z4 E11891.661494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X114.428 Y116.607 Z4 E11898.486598 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X113.11 Y115.676 Z4 E11905.195399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X112.39 Y114.896 Z4 E11909.608638 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X111.818 Y114.018 Z4 E11913.965248 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X111.264 Y112.574 Z4 E11920.395371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X111.107 Y111.569 Z4 E11924.624353 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X111.12 Y110.566 Z4 E11928.794693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X111.447 Y109.122 Z4 E11934.950156 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X111.856 Y108.24 Z4 E11938.992162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X112.4 Y107.45 Z4 E11942.979991 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X113.06 Y106.771 Z4 E11946.91679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X114.22 Y105.997 Z4 E11952.714516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X115.509 Y105.547 Z4 E11958.390738 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X116.842 Y105.437 Z4 E11963.951546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X117.711 Y105.549 Z4 E11967.594311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X118.927 Y105.979 Z4 E11972.956631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X119.973 Y106.683 Z4 E11978.198619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X120.79 Y107.606 Z4 E11983.323368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X121.337 Y108.678 Z4 E11988.326907 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X121.59 Y109.826 Z4 E11993.214267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X121.549 Y110.972 Z4 E11997.98183 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X121.365 Y111.699 Z4 E12001.099649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X121.146106 Y112.192427 Z4 E12003.343879 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044
G1 X121.066 Y112.373 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=end-early tail
G1 X120.431 Y113.247 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=end-early tail
G1 X119.905 Y113.717 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=end-early tail
G1 X119.318 Y114.086 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=end-early tail
G1 X118.365 Y114.432 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=end-early tail
G1 X117.71 Y114.522 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=end-early tail
G1 X117.062 Y114.5 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0044 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0044
G0 X117.062 Y114.5 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0043 note=intra-page lift
G0 X163.959584 Y125.533412 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0043 note=intra-page XY
G0 X163.959584 Y125.533412 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0043 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0043
G1 X164.106 Y127.02 Z4 E12003.653113 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X164.10539 Y127.026189 Z4 E12003.655693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X163.959584 Y128.506588 Z4 E12004.580814 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X163.955973 Y128.51849 Z4 E12004.591134 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X163.525962 Y129.936048 Z4 E12006.126982 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X163.517167 Y129.952501 Z4 E12006.150203 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X162.821798 Y131.253445 Z4 E12008.291618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X162.806018 Y131.272674 Z4 E12008.332899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X161.874154 Y132.408154 Z4 E12011.074721 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X161.850118 Y132.427879 Z4 E12011.139223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X160.719445 Y133.355798 Z4 E12014.476291 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X160.686538 Y133.373388 Z4 E12014.569175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X159.402048 Y134.059962 Z4 E12018.496328 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X159.360391 Y134.072599 Z4 E12018.622754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X157.972588 Y134.493584 Z4 E12023.134833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X157.923078 Y134.49846 Z4 E12023.29996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X156.486 Y134.64 Z4 E12028.391805 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X156.4303 Y134.634514 Z4 E12028.600794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X154.999412 Y134.493584 Z4 E12034.267245 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X154.939902 Y134.475532 Z4 E12034.525256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=prime ramp
G1 X153.569952 Y134.059962 Z4 E12040.47713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X152.252555 Y133.355798 Z4 E12046.68755 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X151.097846 Y132.408154 Z4 E12052.897971 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X150.150202 Y131.253445 Z4 E12059.108391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X149.446038 Y129.936048 Z4 E12065.318812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X149.012416 Y128.506588 Z4 E12071.529233 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X148.866 Y127.02 Z4 E12077.739653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X149.012416 Y125.533412 Z4 E12083.950074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X149.446038 Y124.103952 Z4 E12090.160495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X150.150202 Y122.786555 Z4 E12096.370915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X151.097846 Y121.631846 Z4 E12102.581336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X152.252555 Y120.684202 Z4 E12108.791756 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X153.569952 Y119.980038 Z4 E12115.002177 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X154.999412 Y119.546416 Z4 E12121.212598 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X156.486 Y119.4 Z4 E12127.423018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X157.972588 Y119.546416 Z4 E12133.633439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X159.402048 Y119.980038 Z4 E12139.84386 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X160.719445 Y120.684202 Z4 E12146.05428 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X161.473227 Y121.302814 Z4 E12150.108378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043
G1 X161.874154 Y121.631846 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=end-early tail
G1 X162.821798 Y122.786555 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=end-early tail
G1 X163.525962 Y124.103952 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=end-early tail
G1 X163.959584 Y125.533412 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0043 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0043
G0 X163.959584 Y125.533412 Z8.04532 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0042 note=intra-page lift
G0 X176.899899 Y121.958485 Z8.04532 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0042 note=intra-page XY
G0 X176.899899 Y121.958485 Z4.04532 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0042 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0042
G1 X177.561025 Y121.72193 Z4.396403 E12150.193789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.04532 matz1=4.396403 note=collision lift
G1 X177.561195 Y121.721869 Z4.396313 E12150.193832 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.396403 matz1=4.396313 note=collision lift
G1 X177.902663 Y121.59969 Z4.577646 E12150.304867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.396313 matz1=4.577646 note=collision lift
G1 X177.906768 Y121.598221 Z4.58001 E12150.306507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.577646 matz1=4.58001 note=collision lift
G1 X178.170797 Y121.532085 Z4.716102 E12150.420192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.58001 matz1=4.716102 note=collision lift
G1 X178.587897 Y121.427607 Z4.931094 E12150.652089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.716102 matz1=4.931094 note=collision lift
G1 X178.588072 Y121.427563 Z4.931004 E12150.652199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.931094 matz1=4.931004 note=collision lift
G1 X178.935644 Y121.340501 Z5.110157 E12150.894391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.931004 matz1=5.110157 note=collision lift
G1 X178.944101 Y121.338383 Z5.114701 E12150.900894 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.110157 matz1=5.114701 note=collision lift
G1 X179.482581 Y121.258507 Z5.386885 E12151.355633 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.114701 matz1=5.386885 note=collision lift
G1 X179.638673 Y121.235353 Z5.465784 E12151.506645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.386885 matz1=5.465784 note=collision lift
G1 X179.638852 Y121.235326 Z5.465694 E12151.506823 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.465784 matz1=5.465694 note=collision lift
G1 X179.988973 Y121.183391 Z5.642669 E12151.87695 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.465694 matz1=5.642669 note=collision lift
G1 X180.001907 Y121.181472 Z5.649391 E12151.891537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.642669 matz1=5.649391 note=collision lift
G1 X180.703234 Y121.147018 Z6.000475 E12152.757459 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.649391 matz1=6 note=collision lift
G1 X180.704183 Y121.146971 Z6 E12152.758746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X180.830857 Y121.140748 Z6 E12152.914702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y121.129 Z6 E12153.221279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y121.181472 Z6 E12154.784518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X182.327211 Y121.209525 Z6 E12155.097399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y121.338383 Z6 E12156.664719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X183.799071 Y121.489469 Z6 E12157.903723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y121.598221 Z6 E12158.861883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X185.224137 Y121.952773 Z6 E12161.333674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y121.958485 Z6 E12161.376009 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y122.415704 Z6 E12164.207097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X186.520961 Y122.603999 Z6 E12165.249603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X186.521775 Y122.604487 Z6.000475 E12165.252679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X186.557329 Y122.625797 Z5.979749 E12165.387253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=5.979303 note=collision lift
G1 X187.124049 Y122.965476 Z5.649391 E12167.612711 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.979303 matz1=5.649391 note=collision lift
G1 X187.670969 Y123.371099 Z5.308931 E12170.064459 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.649391 matz1=5.308931 note=collision lift
G1 X187.982908 Y123.602449 Z5.114747 E12171.534768 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.308931 matz1=5.114747 note=collision lift
G1 X187.982984 Y123.602505 Z5.114701 E12171.535129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X188.689243 Y124.242622 Z4.638111 E12175.365293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.114701 matz1=4.638111 note=collision lift
G1 X188.775343 Y124.320657 Z4.58001 E12175.85375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.638111 matz1=4.58001 note=collision lift
G1 X189.493495 Y125.113016 Z4.04532 E12180.568573 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X189.547489 Y125.185819 Z4 E12180.98641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.04532 matz1=4 note=collision lift
G1 X189.591059 Y125.244566 Z4 E12181.289755 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 note=prime ramp
G1 X190.130524 Y125.971951 Z4 E12185.054803 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X190.680296 Y126.88919 Z4 E12189.500772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.137515 Y127.855899 Z4 E12193.946741 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.497779 Y128.862768 Z4 E12198.39271 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.757617 Y129.900101 Z4 E12202.838679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.914528 Y130.957907 Z4 E12207.284648 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.967 Y132.026 Z4 E12211.730618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.914528 Y133.094093 Z4 E12216.176587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.757617 Y134.151899 Z4 E12220.622556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.497779 Y135.189232 Z4 E12225.068525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X191.137515 Y136.196101 Z4 E12229.514494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X190.680296 Y137.16281 Z4 E12233.960463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X190.130524 Y138.080049 Z4 E12238.406432 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X189.493495 Y138.938984 Z4 E12242.852401 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X188.775343 Y139.731343 Z4 E12247.29837 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X187.982984 Y140.449495 Z4 E12251.74434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X187.124049 Y141.086524 Z4 E12256.190309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X186.20681 Y141.636296 Z4 E12260.636278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X185.322038 Y142.054762 Z4 E12264.705412 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X185.240101 Y142.093515 Z4.04532 E12265.126726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4 matz1=4.04532 note=collision lift
G1 X184.233232 Y142.453779 Z4.58001 E12270.097471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.04532 matz1=4.58001 note=collision lift
G1 X183.195899 Y142.713617 Z5.114701 E12275.068215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.58001 matz1=5.114701 note=collision lift
G1 X183.195807 Y142.713631 Z5.114747 E12275.068651 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X182.138093 Y142.870528 Z5.649391 E12280.03896 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.114747 matz1=5.649391 note=collision lift
G1 X181.436766 Y142.904982 Z6.000475 E12283.302826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.649391 matz1=6 note=collision lift
G1 X181.435817 Y142.905029 Z6 E12283.30724 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y142.923 Z6 E12284.829966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y142.870528 Z6 E12289.275935 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y142.713617 Z6 E12293.721905 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y142.453779 Z6 E12298.167874 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y142.093515 Z6 E12302.613843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y141.636296 Z6 E12307.059812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X175.619039 Y141.448001 Z6 E12308.582539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X175.618225 Y141.447513 Z6.000475 E12308.586952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=6 note=collision lift
G1 X175.015951 Y141.086524 Z5.649391 E12311.850818 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=5.649391 note=collision lift
G1 X174.157092 Y140.449551 Z5.114747 E12316.821128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X174.157016 Y140.449495 Z5.114701 E12316.821563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X173.364657 Y139.731343 Z4.58001 E12321.792307 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X172.646505 Y138.938984 Z4.04532 E12326.763052 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X172.592511 Y138.866181 Z4 E12327.184366 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.04532 matz1=4 note=collision lift
G1 X172.009476 Y138.080049 Z4 E12331.2535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X171.459704 Y137.16281 Z4 E12335.69947 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X171.002485 Y136.196101 Z4 E12340.145439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X170.642221 Y135.189232 Z4 E12344.591408 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X170.382383 Y134.151899 Z4 E12349.037377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X170.225472 Y133.094093 Z4 E12353.483346 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X170.173 Y132.026 Z4 E12357.929315 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X170.225472 Y130.957907 Z4 E12362.375284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X170.382383 Y129.900101 Z4 E12366.821253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X170.642221 Y128.862768 Z4 E12371.267222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X171.002485 Y127.855899 Z4 E12375.713192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X171.459704 Y126.88919 Z4 E12380.159161 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X172.009476 Y125.971951 Z4 E12384.60513 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X172.646505 Y125.113016 Z4 E12389.051099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X172.650125 Y125.109022 Z4 E12389.073512 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042
G1 X173.227572 Y124.471908 Z4.42993 E12393.070352 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4 matz1=4.42993 note=collision lift
G1 X173.364657 Y124.320657 Z4.531995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.42993 matz1=4.531995 note=collision lift
G1 X174.157016 Y123.602505 Z5.066685 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=4.531995 matz1=5.066685 note=collision lift
G1 X175.015951 Y122.965476 Z5.601376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.066685 matz1=5.601376 note=collision lift
G1 X175.777627 Y122.508945 Z6.045383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.601376 matz1=6 note=collision lift
G1 X175.93319 Y122.415704 Z5.9547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=6 matz1=5.9547 note=collision lift
G1 X176.8184 Y121.997031 Z5.465087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.9547 matz1=5.465087 note=collision lift
G1 X176.818432 Y121.997015 Z5.465087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.465087 matz1=5.465087 note=collision lift
G1 X176.899899 Y121.958485 Z5.46487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0042 matz0=5.465087 matz1=5.46487 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0042
G0 X176.899899 Y121.958485 Z9.46487 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0041 note=intra-page lift
G0 X171.002485 Y106.519899 Z9.46487 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0041 note=intra-page XY
G0 X171.002485 Y106.519899 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0041 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0041
G1 X171.459704 Y105.55319 Z4 E12393.228833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X171.681086 Y105.183835 Z4 E12393.382166 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X172.009476 Y104.635951 Z4 E12393.704277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X172.522515 Y103.944198 Z4 E12394.317607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X172.646505 Y103.777016 Z4 E12394.496682 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X173.364657 Y102.984657 Z4 E12395.60605 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X173.529502 Y102.835251 Z4 E12395.876676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X174.157016 Y102.266505 Z4 E12397.032381 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X174.681588 Y101.877457 Z4 E12398.059372 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X175.015951 Y101.629476 Z4 E12398.775673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X175.93319 Y101.079704 Z4 E12400.835928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X175.946147 Y101.073576 Z4 E12400.865696 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X176.817962 Y100.661238 Z4 E12402.999361 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=prime ramp
G1 X176.899899 Y100.622485 Z4.04532 E12403.238529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4 matz1=4.04532 note=collision lift
G1 X177.265603 Y100.491634 Z4.239524 E12404.295648 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.04532 matz1=4.239524 note=collision lift
G1 X177.906768 Y100.262221 Z4.58001 E12406.275173 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.239524 matz1=4.58001 note=collision lift
G1 X178.547637 Y100.101692 Z4.910345 E12408.349227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.58001 matz1=4.910345 note=collision lift
G1 X178.944101 Y100.002383 Z5.114701 E12409.70802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.910345 matz1=5.114701 note=collision lift
G1 X178.944193 Y100.002369 Z5.114747 E12409.708338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X179.866932 Y99.865494 Z5.581165 E12413.026433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.114747 matz1=5.581165 note=collision lift
G1 X180.001907 Y99.845472 Z5.649391 E12413.537069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.581165 matz1=5.649391 note=collision lift
G1 X180.703234 Y99.811018 Z6.000475 E12416.266767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.649391 matz1=6 note=collision lift
G1 X180.704183 Y99.810971 Z6 E12416.270574 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y99.793 Z6 E12417.602635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X181.264835 Y99.802572 Z6 E12418.327267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y99.845472 Z6 E12421.704671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X182.757009 Y99.93728 Z6 E12424.251729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y100.002383 Z6 E12426.096386 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y100.262221 Z6 E12430.542355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y100.622485 Z6 E12434.988324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y101.079704 Z6 E12439.434293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X186.520961 Y101.267999 Z6 E12440.95702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X186.521775 Y101.268487 Z6.000475 E12440.961434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X187.124049 Y101.629476 Z5.649391 E12444.2253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=5.649391 note=collision lift
G1 X187.982908 Y102.266449 Z5.114747 E12449.195609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X187.982984 Y102.266505 Z5.114701 E12449.196044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X188.775343 Y102.984657 Z4.58001 E12454.166789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X189.493495 Y103.777016 Z4.04532 E12459.137533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X189.547489 Y103.849819 Z4 E12459.558847 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.04532 matz1=4 note=collision lift
G1 X190.130524 Y104.635951 Z4 E12463.627982 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X190.680296 Y105.55319 Z4 E12468.073951 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.137515 Y106.519899 Z4 E12472.51992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.497779 Y107.526768 Z4 E12476.965889 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.757617 Y108.564101 Z4 E12481.411858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.914528 Y109.621907 Z4 E12485.857827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.967 Y110.69 Z4 E12490.303797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.914528 Y111.758093 Z4 E12494.749766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.757617 Y112.815899 Z4 E12499.195735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.497779 Y113.853232 Z4 E12503.641704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X191.137515 Y114.860101 Z4 E12508.087673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X190.972298 Y115.209425 Z4 E12509.694239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X190.680296 Y115.82681 Z4.341478 E12512.868788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4 matz1=4.341478 note=collision lift
G1 X190.130524 Y116.744049 Z4.876169 E12517.839533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X189.493495 Y117.602984 Z5.410859 E12522.810277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X188.775343 Y118.395343 Z5.94555 E12527.781022 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X187.982984 Y119.113495 Z6.48024 E12532.751767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.94555 matz1=6 note=collision lift
G1 X187.124049 Y119.750524 Z7.014931 E12537.722511 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y120.300296 Z7.549621 E12542.693256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X185.392535 Y120.68542 Z8 E12546.8802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y120.757515 Z8 E12547.581252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y121.117779 Z8 E12552.027221 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y121.377617 Z8 E12556.473191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y121.534528 Z8 E12560.91916 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y121.587 Z8 E12565.365129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y121.534528 Z8 E12569.811098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X179.494006 Y121.459188 Z8 E12571.94581 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X179.492795 Y121.459008 Z8 E12571.950899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y121.377617 Z7.737636 E12574.502021 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.93186 Y121.374551 Z7.731326 E12574.560678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.760973 Y121.331746 Z7.649543 E12575.368168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.753434 Y121.329858 Z7.645657 E12575.404292 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.748402 Y121.328597 Z7.643163 E12575.428222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.747407 Y121.328348 Z7.643676 E12575.432992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.389745 Y121.238758 Z7.467151 E12577.132547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.388677 Y121.238491 Z7.467701 E12577.13766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X178.080965 Y121.161413 Z7.309092 E12578.61217 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y121.117779 Z7.398881 E12579.446899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X177.782491 Y121.073312 Z7.464878 E12580.060434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X177.578256 Y121.000235 Z7.465085 E12580.962262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X177.567579 Y120.996415 Z7.470754 E12581.01497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X177.22082 Y120.872343 Z7.510268 E12582.554921 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X177.211617 Y120.86905 Z7.505381 E12582.600356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X177.062333 Y120.815635 Z7.502615 E12583.259638 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X177.060359 Y120.814929 Z7.503663 E12583.269383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y120.757515 Z7.477489 E12583.986227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X176.877481 Y120.746913 Z7.46509 E12584.101497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X176.804019 Y120.712167 Z7.464886 E12584.439358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y120.300296 Z6.983227 E12588.917094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X175.015951 Y119.750524 Z6.448537 E12593.887839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=6 note=collision lift
G1 X174.157016 Y119.113495 Z5.913847 E12598.858583 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=6 matz1=5.913847 note=collision lift
G1 X173.364657 Y118.395343 Z5.379156 E12603.829328 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.913847 matz1=5.379156 note=collision lift
G1 X172.646505 Y117.602984 Z4.844466 E12608.800072 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=5.379156 matz1=4.844466 note=collision lift
G1 X172.009476 Y116.744049 Z4.309775 E12613.770817 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.844466 matz1=4.309775 note=collision lift
G1 X171.690963 Y116.212643 Z4 E12616.650639 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 matz0=4.309775 matz1=4 note=collision lift
G1 X171.459704 Y115.82681 Z4 E12618.520817 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X171.002485 Y114.860101 Z4 E12622.966786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X170.642221 Y113.853232 Z4 E12627.412755 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X170.382383 Y112.815899 Z4 E12631.858724 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X170.225472 Y111.758093 Z4 E12636.304694 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X170.20845 Y111.411606 Z4 E12637.746955 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041
G1 X170.173 Y110.69 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=end-early tail
G1 X170.225472 Y109.621907 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=end-early tail
G1 X170.382383 Y108.564101 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=end-early tail
G1 X170.642221 Y107.526768 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=end-early tail
G1 X171.002485 Y106.519899 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0041 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0041
G0 X171.002485 Y106.519899 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0040 note=intra-page lift
G0 X161.807268 Y102.341804 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0040 note=intra-page XY
G0 X161.807268 Y102.341804 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0040 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0040
G1 X161.92439 Y102.351531 Z4 E12637.748869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X163.28898 Y102.573181 Z4 E12638.058769 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X163.308547 Y102.576359 Z4 E12638.067064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X164.537331 Y102.891744 Z4 E12638.824496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X164.735741 Y102.965182 Z4 E12638.99421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X165.61851 Y103.291924 Z4 E12639.899693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X166.116408 Y103.545391 Z4 E12640.553279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X166.559852 Y103.771138 Z4 E12641.208225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X167.369125 Y104.323625 Z4 E12642.698592 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X167.385822 Y104.338738 Z4 E12642.735975 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X168.054097 Y104.943624 Z4 E12644.347565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X168.437453 Y105.403395 Z4 E12645.542299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X168.622537 Y105.625373 Z4 E12646.15467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.082212 Y106.363112 Z4 E12648.135926 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.223799 Y106.674157 Z4 E12648.97225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.440891 Y107.151078 Z4 E12650.317441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.706341 Y107.983511 Z4 E12652.729672 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.727032 Y108.083657 Z4 E12653.025829 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.88633 Y108.85465 Z4 E12655.402908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.938486 Y109.565462 Z4 E12657.703036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X170.021 Y110.69 Z4 E12661.629515 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.993745 Y111.06144 Z4 E12663.00387 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.88633 Y112.52535 Z4 E12668.79479 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.879824 Y112.556839 Z4 E12668.928331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=prime ramp
G1 X169.706341 Y113.396489 Z4 E12672.492919 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X169.440891 Y114.228922 Z4 E12676.125478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X169.082212 Y115.016888 Z4 E12679.724892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X168.622537 Y115.754627 Z4 E12683.338727 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X168.054097 Y116.436376 Z4 E12687.029108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X167.369125 Y117.056375 Z4 E12690.870225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X166.559852 Y117.608862 Z4 E12694.944093 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X165.61851 Y118.088076 Z4 E12699.335681 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X164.537331 Y118.488256 Z4 E12704.128726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X163.308547 Y118.803641 Z4 E12709.403004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X161.92439 Y119.028469 Z4 E12715.233079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X160.377092 Y119.156979 Z4 E12721.688146 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X158.658885 Y119.183409 Z4 E12728.832467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X156.762 Y119.102 Z4 E12736.726056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X154.96157 Y119.325758 Z4 E12744.268959 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X152.301313 Y119.382313 Z4 E12755.331525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X148.915898 Y119.173086 Z4 E12769.433295 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X144.94 Y118.5995 Z4 E12786.134289 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X142.772704 Y118.145267 Z4 E12795.34063 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X140.508289 Y117.562977 Z4 E12805.061254 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X138.163589 Y116.840308 Z4 E12815.261898 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X135.755438 Y115.964938 Z4 E12825.914772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X133.300669 Y114.924544 Z4 E12836.999298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X130.816117 Y113.706805 Z4 E12848.502844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X128.318616 Y112.299397 Z4 E12860.421442 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X125.825 Y110.69 Z4 E12872.760433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X128.318616 Y109.080603 Z4 E12885.099423 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X130.816117 Y107.673195 Z4 E12897.018022 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X133.300669 Y106.455456 Z4 E12908.521568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X135.755438 Y105.415063 Z4 E12919.606094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X138.163589 Y104.539692 Z4 E12930.258968 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X140.508289 Y103.817023 Z4 E12940.459611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X142.772704 Y103.234733 Z4 E12950.180235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X144.94 Y102.7805 Z4 E12959.386577 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X148.915898 Y102.206914 Z4 E12976.087571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X152.301313 Y101.997688 Z4 E12990.189341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X154.96157 Y102.054242 Z4 E13001.251907 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X156.762 Y102.278 Z4 E13008.79481 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X156.814093 Y102.275764 Z4 E13009.011588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040
G1 X158.658885 Y102.196591 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=end-early tail
G1 X160.377092 Y102.223021 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=end-early tail
G1 X161.807268 Y102.341804 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0040 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0040
G0 X161.807268 Y102.341804 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0039 note=intra-page lift
G0 X162.821798 Y90.126555 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0039 note=intra-page XY
G0 X162.821798 Y90.126555 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0039 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0039
G1 X163.525962 Y91.443952 Z4 E13009.320821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X163.527767 Y91.449903 Z4 E13009.323401 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X163.959584 Y92.873412 Z4 E13010.248522 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X163.960803 Y92.885789 Z4 E13010.258843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X164.106 Y94.36 Z4 E13011.79469 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X164.104171 Y94.378567 Z4 E13011.817911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X163.959584 Y95.846588 Z4 E13013.959326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X163.952363 Y95.870392 Z4 E13014.000608 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X163.525962 Y97.276048 Z4 E13016.742429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X163.511304 Y97.30347 Z4 E13016.806932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X162.821798 Y98.593445 Z4 E13020.143999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X162.798128 Y98.622288 Z4 E13020.236883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X161.874154 Y99.748154 Z4 E13024.164037 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X161.840503 Y99.77577 Z4 E13024.290462 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X160.719445 Y100.695798 Z4 E13028.802542 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X160.675569 Y100.719251 Z4 E13028.967669 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X159.402048 Y101.399962 Z4 E13034.059514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X159.348489 Y101.416209 Z4 E13034.268503 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X157.972588 Y101.833584 Z4 E13039.934953 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X157.9107 Y101.839679 Z4 E13040.192964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=prime ramp
G1 X156.486 Y101.98 Z4 E13046.144838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X154.999412 Y101.833584 Z4 E13052.355259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X153.569952 Y101.399962 Z4 E13058.565679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X152.252555 Y100.695798 Z4 E13064.7761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X151.097846 Y99.748154 Z4 E13070.98652 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X150.150202 Y98.593445 Z4 E13077.196941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X149.446038 Y97.276048 Z4 E13083.407362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X149.012416 Y95.846588 Z4 E13089.617782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X148.866 Y94.36 Z4 E13095.828203 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X149.012416 Y92.873412 Z4 E13102.038624 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X149.446038 Y91.443952 Z4 E13108.249044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X150.150202 Y90.126555 Z4 E13114.459465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X151.097846 Y88.971846 Z4 E13120.669885 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X152.252555 Y88.024202 Z4 E13126.880306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X153.569952 Y87.320038 Z4 E13133.090727 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X154.999412 Y86.886416 Z4 E13139.301147 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X156.486 Y86.74 Z4 E13145.511568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X157.972588 Y86.886416 Z4 E13151.721989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X158.905725 Y87.16948 Z4 E13155.776087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039
G1 X159.402048 Y87.320038 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=end-early tail
G1 X160.719445 Y88.024202 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=end-early tail
G1 X161.874154 Y88.971846 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=end-early tail
G1 X162.821798 Y90.126555 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0039 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0039
G0 X162.821798 Y90.126555 Z9.128864 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0038 note=intra-page lift
G0 X178.972051 Y78.662237 Z9.128864 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0038 note=intra-page XY
G0 X178.972051 Y78.662237 Z5.128864 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0038 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0038
G1 X179.638673 Y78.563353 Z5.465747 E13155.854754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.128864 matz1=5.465747 note=collision lift
G1 X179.638815 Y78.563332 Z5.465675 E13155.854788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.465747 matz1=5.465675 note=collision lift
G1 X180.001739 Y78.509497 Z5.649121 E13155.963785 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.465675 matz1=5.649121 note=collision lift
G1 X180.001907 Y78.509472 Z5.649391 E13155.963888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.649121 matz1=5.649391 note=collision lift
G1 X180.301977 Y78.494731 Z5.799606 E13156.087901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.649391 matz1=5.799403 note=collision lift
G1 X180.703234 Y78.475018 Z6.000475 E13156.302598 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.799403 matz1=6 note=collision lift
G1 X180.704183 Y78.474971 Z6 E13156.303171 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y78.457 Z6 E13156.519738 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X181.752697 Y78.490539 Z6 E13157.023342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y78.509472 Z6 E13157.364819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y78.666383 Z6 E13158.526862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X183.239317 Y78.677258 Z6 E13158.582411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y78.926221 Z6 E13160.005868 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X184.680822 Y79.086371 Z6 E13160.765107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y79.286485 Z6 E13161.801836 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X186.059113 Y79.673848 Z6 E13163.571431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y79.743704 Z6 E13163.914766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X186.520961 Y79.931999 Z6 E13164.711305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X186.521775 Y79.932487 Z6.000475 E13164.713668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X187.124049 Y80.293476 Z5.649391 E13166.546488 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=5.649391 note=collision lift
G1 X187.256412 Y80.391643 Z5.566995 E13167.001382 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.649391 matz1=5.566995 note=collision lift
G1 X187.982908 Y80.930449 Z5.114747 E13169.66569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.566995 matz1=5.114747 note=collision lift
G1 X187.982984 Y80.930505 Z5.114701 E13169.66598 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X188.306818 Y81.224012 Z4.896174 E13171.054961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.114701 matz1=4.896174 note=collision lift
G1 X188.775343 Y81.648657 Z4.58001 E13173.181676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.896174 matz1=4.58001 note=collision lift
G1 X189.251688 Y82.174224 Z4.225354 E13175.732168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.58001 matz1=4.225354 note=collision lift
G1 X189.493495 Y82.441016 Z4.04532 E13177.093575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.225354 matz1=4.04532 note=collision lift
G1 X189.547489 Y82.513819 Z4 E13177.443356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.04532 matz1=4 note=collision lift
G1 X190.130524 Y83.299951 Z4 E13180.968116 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 note=prime ramp
G1 X190.139445 Y83.314835 Z4 E13181.033002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 note=prime ramp
G1 X190.680296 Y84.21719 Z4 E13185.122826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 note=prime ramp
G1 X190.871828 Y84.622151 Z4 E13186.957463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 note=prime ramp
G1 X191.137515 Y85.183899 Z4 E13189.540984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X191.497779 Y86.190768 Z4 E13193.986953 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X191.757617 Y87.228101 Z4 E13198.432922 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X191.914528 Y88.285907 Z4 E13202.878891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X191.967 Y89.354 Z4 E13207.324861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X191.914528 Y90.422093 Z4 E13211.77083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X191.757617 Y91.479899 Z4 E13216.216799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X191.497779 Y92.517232 Z4 E13220.662768 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X191.137515 Y93.524101 Z4 E13225.108737 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X190.972298 Y93.873425 Z4 E13226.715303 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X190.680296 Y94.49081 Z4.341478 E13229.889852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4 matz1=4.341478 note=collision lift
G1 X190.130524 Y95.408049 Z4.876169 E13234.860597 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X189.493495 Y96.266984 Z5.410859 E13239.831341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X188.775343 Y97.059343 Z5.94555 E13244.802086 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X187.982984 Y97.777495 Z6.48024 E13249.772831 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.94555 matz1=6 note=collision lift
G1 X187.124049 Y98.414524 Z7.014931 E13254.743575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y98.964296 Z7.549621 E13259.71432 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X185.392535 Y99.34942 Z8 E13263.901264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y99.421515 Z8 E13264.602316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y99.781779 Z8 E13269.048286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y100.041617 Z8 E13273.494255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y100.198528 Z8 E13277.940224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y100.251 Z8 E13282.386193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y100.198528 Z8 E13286.832162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X179.494006 Y100.123188 Z8 E13288.966874 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X179.492795 Y100.123008 Z8 E13288.971964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y100.041617 Z7.737636 E13291.523085 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.93186 Y100.038551 Z7.731326 E13291.581742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.766661 Y99.997171 Z7.652265 E13292.362356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.760973 Y99.995746 Z7.655196 E13292.389611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y99.781779 Z7.220833 E13296.471861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y99.421515 Z6.686142 E13301.442606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y98.964296 Z6.151452 E13306.41335 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X175.015951 Y98.414524 Z5.616761 E13311.384095 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=5.616761 note=collision lift
G1 X174.157016 Y97.777495 Z5.082071 E13316.354839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X173.364657 Y97.059343 Z4.547381 E13321.325584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X172.646505 Y96.266984 Z4.01269 E13326.296329 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X172.631386 Y96.246598 Z4 E13326.414302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.01269 matz1=4 note=collision lift
G1 X172.009476 Y95.408049 Z4 E13330.754752 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X171.459704 Y94.49081 Z4 E13335.200722 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X171.002485 Y93.524101 Z4 E13339.646691 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X170.642221 Y92.517232 Z4 E13344.09266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X170.382383 Y91.479899 Z4 E13348.538629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X170.225472 Y90.422093 Z4 E13352.984598 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X170.173 Y89.354 Z4 E13357.430567 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X170.225472 Y88.285907 Z4 E13361.876536 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X170.382383 Y87.228101 Z4 E13366.322505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X170.642221 Y86.190768 Z4 E13370.768475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X171.002485 Y85.183899 Z4 E13375.214444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X171.459704 Y84.21719 Z4 E13379.660413 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X172.009476 Y83.299951 Z4 E13384.106382 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X172.646505 Y82.441016 Z4 E13388.552351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X173.326212 Y81.691076 Z4 E13392.760308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038
G1 X173.364657 Y81.648657 Z4.028624 E13393.026414 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4 matz1=4.028624 note=collision lift
G1 X174.157016 Y80.930505 Z4.563315 E13397.997158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.028624 matz1=4.563315 note=collision lift
G1 X174.99062 Y80.312262 Z5.082237 E13402.821311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=4.563315 matz1=5.082237 note=collision lift
G1 X175.015951 Y80.293476 Z5.098005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.082237 matz1=5.098005 note=collision lift
G1 X175.93319 Y79.743704 Z5.632696 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.098005 matz1=5.632696 note=collision lift
G1 X176.817962 Y79.325238 Z6.122066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=5.632696 matz1=6 note=collision lift
G1 X176.899899 Y79.286485 Z6.212706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X177.762545 Y78.977825 Z7.12891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y78.926221 Z7.12891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.587897 Y78.755607 Z7.128907 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.588072 Y78.755563 Z7.128727 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y78.666383 Z7.128725 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.944316 Y78.666351 Z7.128507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
G1 X178.972051 Y78.662237 Z7.128507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0038 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0038
G0 X178.972051 Y78.662237 Z11.128507 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0037 note=intra-page lift
G0 X175.626517 Y56.108484 Z11.128507 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0037 note=intra-page XY
G0 X175.626517 Y56.108484 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0037 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0037
G1 X175.618228 Y56.103515 Z6 E13402.821324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X175.618225 Y56.103513 Z6.000761 E13402.821326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X175.61692 Y56.102731 Z6 E13402.821331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X175.015951 Y55.742524 Z6 E13402.891719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X174.383648 Y55.273577 Z6 E13403.133125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X174.157016 Y55.105495 Z6 E13403.261466 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X173.364657 Y54.387343 Z6 E13403.948175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X173.264957 Y54.277341 Z6 E13404.068566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X172.755234 Y53.714948 Z6 E13404.779528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X172.755202 Y53.714913 Z6.000025 E13404.779584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X172.646505 Y53.594984 Z5.919096 E13404.972666 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=5.919096 note=collision lift
G1 X172.519608 Y53.423883 Z5.812586 E13405.240615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.919096 matz1=5.812586 note=collision lift
G1 X172.427867 Y53.300184 Z5.735612 E13405.444108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.812586 matz1=5.735612 note=collision lift
G1 X172.427759 Y53.300039 Z5.735702 E13405.444351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.735612 matz1=5.735702 note=collision lift
G1 X172.348141 Y53.192687 Z5.668875 E13405.627635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.735702 matz1=5.668875 note=collision lift
G1 X172.009476 Y52.736049 Z5.384619 E13406.476406 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.668875 matz1=5.384619 note=collision lift
G1 X171.612011 Y52.072918 Z4.998057 E13407.810331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.384619 matz1=4.998057 note=collision lift
G1 X171.459704 Y51.81881 Z4.849928 E13408.376365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.998057 matz1=4.849928 note=collision lift
G1 X171.012745 Y50.873794 Z4.327236 E13410.616655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.849928 matz1=4.327236 note=collision lift
G1 X171.002485 Y50.852101 Z4.315238 E13410.672527 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.327236 matz1=4.315238 note=collision lift
G1 X170.911552 Y50.597962 Z4.180279 E13411.314714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.315238 matz1=4.180279 note=collision lift
G1 X170.642221 Y49.845232 Z4.58001 E13413.364892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.180279 matz1=4.58001 note=collision lift
G1 X170.581898 Y49.604409 Z4.704142 E13414.046607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.58001 matz1=4.704142 note=collision lift
G1 X170.382383 Y48.807899 Z5.114701 E13416.453459 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.704142 matz1=5.114701 note=collision lift
G1 X170.382369 Y48.807807 Z5.114747 E13416.453747 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X170.306006 Y48.29301 Z5.374962 E13418.100186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.114747 matz1=5.374962 note=collision lift
G1 X170.225472 Y47.750093 Z5.649391 E13419.938229 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.374962 matz1=5.649391 note=collision lift
G1 X170.191018 Y47.048766 Z6.000475 E13422.441869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.649391 matz1=6 note=collision lift
G1 X170.190971 Y47.047817 Z6 E13422.44537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X170.186053 Y46.947694 Z6 E13422.777392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X170.173 Y46.682 Z6 E13423.671965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X170.225472 Y45.613907 Z6 E13427.466068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X170.249625 Y45.451084 Z6 E13428.078226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X170.382383 Y44.556101 Z6 E13431.577133 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X170.52701 Y43.978715 Z6 E13434.002688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X170.642221 Y43.518768 Z6 E13435.974003 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X171.002485 Y42.511899 Z6 E13440.419972 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X171.459704 Y41.54519 Z6 E13444.865941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X171.647999 Y41.231039 Z6 E13446.388668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X171.648487 Y41.230225 Z6.000475 E13446.393081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X172.009476 Y40.627951 Z5.649391 E13449.656947 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=5.649391 note=collision lift
G1 X172.646449 Y39.769092 Z5.114747 E13454.627257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X172.646505 Y39.769016 Z5.114701 E13454.627692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X173.364657 Y38.976657 Z4.58001 E13459.598436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X174.157016 Y38.258505 Z4.04532 E13464.569181 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X174.229819 Y38.204511 Z4 E13464.990495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.04532 matz1=4 note=collision lift
G1 X175.015951 Y37.621476 Z4 E13469.059629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X175.93319 Y37.071704 Z4 E13473.505599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X176.899899 Y36.614485 Z4 E13477.951568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X177.906768 Y36.254221 Z4 E13482.397537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X178.944101 Y35.994383 Z4 E13486.843506 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X180.001907 Y35.837472 Z4 E13491.289475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X181.07 Y35.785 Z4 E13495.735444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X182.138093 Y35.837472 Z4 E13500.181413 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X183.195899 Y35.994383 Z4 E13504.627382 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X184.233232 Y36.254221 Z4 E13509.073351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X185.240101 Y36.614485 Z4 E13513.519321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X186.20681 Y37.071704 Z4 E13517.96529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X187.124049 Y37.621476 Z4 E13522.411259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X187.982984 Y38.258505 Z4 E13526.857228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X188.775343 Y38.976657 Z4 E13531.303197 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X189.493495 Y39.769016 Z4 E13535.749166 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X190.130524 Y40.627951 Z4 E13540.195135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X190.680296 Y41.54519 Z4 E13544.641104 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.137515 Y42.511899 Z4 E13549.087074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.497779 Y43.518768 Z4 E13553.533043 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.757617 Y44.556101 Z4 E13557.979012 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.914528 Y45.613907 Z4 E13562.424981 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.967 Y46.682 Z4 E13566.87095 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.914528 Y47.750093 Z4 E13571.316919 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.757617 Y48.807899 Z4 E13575.762888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.497779 Y49.845232 Z4 E13580.208857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X191.137515 Y50.852101 Z4 E13584.654827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X190.680296 Y51.81881 Z4 E13589.100796 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X190.130524 Y52.736049 Z4 E13593.546765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X189.493495 Y53.594984 Z4 E13597.992734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X188.775343 Y54.387343 Z4 E13602.438703 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X187.982984 Y55.105495 Z4 E13606.884672 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X187.124049 Y55.742524 Z4 E13611.330641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X186.20681 Y56.292296 Z4 E13615.77661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X185.322038 Y56.710762 Z4 E13619.845745 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037
G1 X185.240101 Y56.749515 Z4.04532 E13620.267059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4 matz1=4.04532 note=collision lift
G1 X184.233232 Y57.109779 Z4.58001 E13625.237803 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.04532 matz1=4.58001 note=collision lift
G1 X183.195899 Y57.369617 Z5.114701 E13630.208548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=4.58001 matz1=5.114701 note=collision lift
G1 X183.195807 Y57.369631 Z5.114747 E13630.208983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X182.138093 Y57.526528 Z5.649391 E13635.179293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.114747 matz1=5.649391 note=collision lift
G1 X181.436766 Y57.560982 Z6.000475 E13638.443158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=5.649391 matz1=6 note=collision lift
G1 X181.435817 Y57.561029 Z6 E13638.447572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y57.579 Z6 E13639.970299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X180.366391 Y57.544434 Z6 E13642.899095 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y57.526528 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y57.369617 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y57.109779 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y56.749515 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X176.744713 Y56.676118 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X176.744661 Y56.676093 Z6.000029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X176.744609 Y56.676069 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y56.292296 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
G1 X175.626517 Y56.108484 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0037 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0037
G0 X175.626517 Y56.108484 Z10 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0036 note=intra-page lift
G0 X171.057836 Y63.730868 Z10 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0036 note=intra-page XY
G0 X171.057836 Y63.730868 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0036 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0036
G1 X171.167702 Y63.498575 Z4 E13642.908246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 note=prime ramp
G1 X171.459704 Y62.88119 Z4.341478 E13643.043428 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4 matz1=4.341478 note=collision lift
G1 X171.680176 Y62.513354 Z4.555902 E13643.210909 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.341478 matz1=4.555902 note=collision lift
G1 X172.009476 Y61.963951 Z4.876169 E13643.579717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.555902 matz1=4.876169 note=collision lift
G1 X172.427125 Y61.400816 Z5.226723 E13644.14635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.876169 matz1=5.226723 note=collision lift
G1 X172.646505 Y61.105016 Z5.410859 E13644.512209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.226723 matz1=5.410859 note=collision lift
G1 X173.300179 Y60.383798 Z5.897543 E13645.705419 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.410859 matz1=5.897543 note=collision lift
G1 X173.364657 Y60.312657 Z5.94555 E13645.840903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.897543 matz1=5.94555 note=collision lift
G1 X174.157016 Y59.594505 Z6.48024 E13647.5658 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.94555 matz1=6 note=collision lift
G1 X174.298579 Y59.489515 Z6.568364 E13647.888115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X175.015951 Y58.957476 Z7.014931 E13649.686901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X175.400648 Y58.726897 Z7.239184 E13650.694439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y58.407704 Z7.549621 E13652.204204 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X176.584755 Y58.099536 Z7.910004 E13654.124391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X176.747465 Y58.02258 Z8 E13654.631989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y57.950485 Z8 E13655.065965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y57.590221 Z8 E13658.001654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X177.965707 Y57.575458 Z8 E13658.177969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y57.330383 Z8 E13661.254304 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X179.430161 Y57.258283 Z8 E13662.855176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y57.173472 Z8 E13664.823917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X180.922795 Y57.128232 Z8 E13668.15601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y57.121 Z8 E13668.710492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y57.173472 Z8 E13672.914029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X182.418264 Y57.215031 Z8 E13674.080472 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X182.645994 Y57.248812 Z8 E13675.037623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X182.647205 Y57.248992 Z8 E13675.042713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y57.330383 Z7.737636 E13677.593834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X183.20814 Y57.333449 Z7.731326 E13677.652491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X183.373339 Y57.374829 Z7.652265 E13678.433106 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X183.379027 Y57.376254 Z7.655196 E13678.46036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y57.590221 Z7.220833 E13682.54261 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y57.950485 Z6.686142 E13687.513355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y58.407704 Z6.151452 E13692.484099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X187.124049 Y58.957476 Z5.616761 E13697.454844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=5.616761 note=collision lift
G1 X187.982984 Y59.594505 Z5.082071 E13702.425589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X188.775343 Y60.312657 Z4.547381 E13707.396333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X189.493495 Y61.105016 Z4.01269 E13712.367078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X189.508614 Y61.125402 Z4 E13712.485051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.01269 matz1=4 note=collision lift
G1 X190.130524 Y61.963951 Z4 E13716.825502 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X190.680296 Y62.88119 Z4 E13721.271471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.137515 Y63.847899 Z4 E13725.71744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.497779 Y64.854768 Z4 E13730.163409 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.757617 Y65.892101 Z4 E13734.609378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.914528 Y66.949907 Z4 E13739.055347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.967 Y68.018 Z4 E13743.501316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.914528 Y69.086093 Z4 E13747.947286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.757617 Y70.143899 Z4 E13752.393255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.497779 Y71.181232 Z4 E13756.839224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X191.137515 Y72.188101 Z4 E13761.285193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X190.972298 Y72.537425 Z4 E13762.891759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X190.680296 Y73.15481 Z4.341478 E13766.066308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4 matz1=4.341478 note=collision lift
G1 X190.130524 Y74.072049 Z4.876169 E13771.037053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X189.493495 Y74.930984 Z5.410859 E13776.007797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X188.775343 Y75.723343 Z5.94555 E13780.978542 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X187.982984 Y76.441495 Z6.48024 E13785.949286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.94555 matz1=6 note=collision lift
G1 X187.124049 Y77.078524 Z7.014931 E13790.920031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y77.628296 Z7.549621 E13795.890776 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X185.392535 Y78.01342 Z8 E13800.07772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y78.085515 Z8 E13800.778772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y78.445779 Z8 E13805.224741 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y78.705617 Z8 E13809.670711 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y78.862528 Z8 E13814.11668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y78.915 Z8 E13818.562649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y78.862528 Z8 E13823.008618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X179.494006 Y78.787188 Z8 E13825.14333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X179.492795 Y78.787008 Z8 E13825.148419 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X179.491518 Y78.786819 Z8 E13825.153787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y78.705617 Z8 E13827.454587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y78.445779 Z8 E13831.900556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y78.085515 Z8 E13836.346525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X176.747465 Y78.01342 Z8 E13837.047577 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y77.628296 Z7.549621 E13841.234522 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X175.015951 Y77.078524 Z7.014931 E13846.205266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X174.157016 Y76.441495 Z6.48024 E13851.176011 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=6 note=collision lift
G1 X173.364657 Y75.723343 Z5.94555 E13856.146756 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=5.94555 note=collision lift
G1 X172.646505 Y74.930984 Z5.410859 E13861.1175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.94555 matz1=5.410859 note=collision lift
G1 X172.009476 Y74.072049 Z4.876169 E13866.088245 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.410859 matz1=4.876169 note=collision lift
G1 X171.459704 Y73.15481 Z4.341478 E13871.058989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.876169 matz1=4.341478 note=collision lift
G1 X171.167702 Y72.537425 Z4 E13874.233539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.341478 matz1=4 note=collision lift
G1 X171.002485 Y72.188101 Z4 E13875.840105 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X170.642221 Y71.181232 Z4 E13880.286074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X170.382383 Y70.143899 Z4 E13884.732043 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X170.225472 Y69.086093 Z4 E13889.178012 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X170.201841 Y68.605081 Z4 E13891.180237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036
G1 X170.176197 Y68.083074 Z4.261318 E13893.609582 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4 matz1=4.261318 note=collision lift
G1 X170.173 Y68.018 Z4.293895 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.261318 matz1=4.293895 note=collision lift
G1 X170.225472 Y66.949907 Z4.828585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.293895 matz1=4.828585 note=collision lift
G1 X170.382383 Y65.892101 Z5.363276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=4.828585 matz1=5.363276 note=collision lift
G1 X170.642221 Y64.854768 Z5.897966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.363276 matz1=5.897966 note=collision lift
G1 X170.711121 Y64.662205 Z6.000225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.897966 matz1=6 note=collision lift
G1 X171.002485 Y63.847899 Z5.567794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=6 matz1=5.567794 note=collision lift
G1 X171.057836 Y63.730868 Z5.503064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0036 matz0=5.567794 matz1=5.503064 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0036
G0 X171.057836 Y63.730868 Z9.503064 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0035 note=intra-page lift
G0 X157.608101 Y57.369617 Z9.503064 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0035 note=intra-page XY
G0 X157.608101 Y57.369617 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0035 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0035
G1 X156.570768 Y57.109779 Z4 E13893.768063 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X156.165321 Y56.964708 Z4 E13893.921395 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X155.563899 Y56.749515 Z4 E13894.243506 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X154.785349 Y56.381288 Z4 E13894.856837 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X154.59719 Y56.292296 Z4 E13895.035912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X153.679951 Y55.742524 Z4 E13896.14528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X153.501256 Y55.609995 Z4 E13896.415905 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X152.821016 Y55.105495 Z4 E13897.57161 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X152.337105 Y54.666903 Z4 E13898.598602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X152.028657 Y54.387343 Z4 E13899.314903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X151.310505 Y53.594984 Z4 E13901.375158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X151.301966 Y53.583471 Z4 E13901.404926 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X150.673476 Y52.736049 Z4 E13903.752375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X150.444724 Y52.3544 Z4 E13904.834877 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X150.123704 Y51.81881 Z4 E13906.446555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X149.749349 Y51.027303 Z4 E13908.888456 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X149.705238 Y50.934038 Z4 E13909.190182 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=prime ramp
G1 X149.666485 Y50.852101 Z4.04532 E13909.489422 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4 matz1=4.04532 note=collision lift
G1 X149.306221 Y49.845232 Z4.58001 E13913.234815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.04532 matz1=4.58001 note=collision lift
G1 X149.284513 Y49.758567 Z4.624682 E13913.565663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.58001 matz1=4.624682 note=collision lift
G1 X149.046383 Y48.807899 Z5.114701 E13917.376411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.624682 matz1=5.114701 note=collision lift
G1 X149.046369 Y48.807807 Z5.114747 E13917.376791 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X148.993325 Y48.45021 Z5.295502 E13918.866497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.114747 matz1=5.295502 note=collision lift
G1 X148.889472 Y47.750093 Z5.649391 E13921.91421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.295502 matz1=5.649391 note=collision lift
G1 X148.85837 Y47.116993 Z5.96632 E13924.790958 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.649391 matz1=5.965892 note=collision lift
G1 X148.855018 Y47.048766 Z6.000475 E13925.108475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.965892 matz1=6 note=collision lift
G1 X148.854971 Y47.047817 Z6 E13925.112889 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X148.837 Y46.682 Z6 E13926.635616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X148.889472 Y45.613907 Z6 E13931.081585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X149.046383 Y44.556101 Z6 E13935.527554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X149.306221 Y43.518768 Z6 E13939.973523 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X149.666485 Y42.511899 Z6 E13944.419492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X150.123704 Y41.54519 Z6 E13948.865461 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X150.311999 Y41.231039 Z6 E13950.388188 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X150.312487 Y41.230225 Z6.000475 E13950.392601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X150.673476 Y40.627951 Z5.649391 E13953.656467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=5.649391 note=collision lift
G1 X151.310449 Y39.769092 Z5.114747 E13958.626777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X151.310505 Y39.769016 Z5.114701 E13958.627212 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X152.028657 Y38.976657 Z4.58001 E13963.597957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X152.821016 Y38.258505 Z4.04532 E13968.568701 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X152.893819 Y38.204511 Z4 E13968.990015 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.04532 matz1=4 note=collision lift
G1 X153.679951 Y37.621476 Z4 E13973.05915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X154.59719 Y37.071704 Z4 E13977.505119 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X155.563899 Y36.614485 Z4 E13981.951088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X156.570768 Y36.254221 Z4 E13986.397057 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X157.608101 Y35.994383 Z4 E13990.843026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X158.665907 Y35.837472 Z4 E13995.288995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X159.734 Y35.785 Z4 E13999.734964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X160.802093 Y35.837472 Z4 E14004.180933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X161.859899 Y35.994383 Z4 E14008.626903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X162.897232 Y36.254221 Z4 E14013.072872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X163.904101 Y36.614485 Z4 E14017.518841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X164.253425 Y36.779702 Z4 E14019.125407 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X164.87081 Y37.071704 Z4.341478 E14022.299956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4 matz1=4.341478 note=collision lift
G1 X165.788049 Y37.621476 Z4.876169 E14027.270701 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X166.646984 Y38.258505 Z5.410859 E14032.241445 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X167.439343 Y38.976657 Z5.94555 E14037.21219 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X168.157495 Y39.769016 Z6.48024 E14042.182934 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.94555 matz1=6 note=collision lift
G1 X168.794524 Y40.627951 Z7.014931 E14047.153679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X169.344296 Y41.54519 Z7.549621 E14052.124424 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X169.72942 Y42.359465 Z8 E14056.311368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X169.801515 Y42.511899 Z8 E14057.01242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.161779 Y43.518768 Z8 E14061.458389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.421617 Y44.556101 Z8 E14065.904358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.578528 Y45.613907 Z8 E14070.350328 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.631 Y46.682 Z8 E14074.796297 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.578528 Y47.750093 Z8 E14079.242266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.503188 Y48.257994 Z8 E14081.376978 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.503008 Y48.259205 Z8 E14081.382067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.421617 Y48.807899 Z7.737636 E14083.933189 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.418551 Y48.82014 Z7.731326 E14083.991845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.377171 Y48.985339 Z7.652265 E14084.77246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.375746 Y48.991027 Z7.655196 E14084.799715 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X170.161779 Y49.845232 Z7.220833 E14088.881965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X169.801515 Y50.852101 Z6.686142 E14093.852709 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X169.344296 Y51.81881 Z6.151452 E14098.823454 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=6 note=collision lift
G1 X168.794524 Y52.736049 Z5.616761 E14103.794199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=6 matz1=5.616761 note=collision lift
G1 X168.157495 Y53.594984 Z5.082071 E14108.764943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X167.439343 Y54.387343 Z4.547381 E14113.735688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X166.646984 Y55.105495 Z4.01269 E14118.706432 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X166.626598 Y55.120614 Z4 E14118.824405 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 matz0=4.01269 matz1=4 note=collision lift
G1 X165.788049 Y55.742524 Z4 E14123.164856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X164.87081 Y56.292296 Z4 E14127.610825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X163.904101 Y56.749515 Z4 E14132.056794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X162.897232 Y57.109779 Z4 E14136.502764 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X162.560724 Y57.19407 Z4 E14137.945025 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035
G1 X161.859899 Y57.369617 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=end-early tail
G1 X160.802093 Y57.526528 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=end-early tail
G1 X159.734 Y57.579 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=end-early tail
G1 X158.665907 Y57.526528 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=end-early tail
G1 X157.608101 Y57.369617 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0035 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0035
G0 X157.608101 Y57.369617 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0034 note=intra-page lift
G0 X155.361038 Y68.267048 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0034 note=intra-page XY
G0 X155.361038 Y68.267048 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0034 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0034
G1 X154.927416 Y66.837588 Z4 E14138.254258 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X154.926807 Y66.831399 Z4 E14138.256838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X154.781 Y65.351 Z4 E14139.181959 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X154.782219 Y65.338622 Z4 E14139.19228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X154.927416 Y63.864412 Z4 E14140.728128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X154.932832 Y63.846559 Z4 E14140.751349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X155.361038 Y62.434952 Z4 E14142.892763 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X155.372764 Y62.413014 Z4 E14142.934045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X156.065202 Y61.117555 Z4 E14145.675866 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X156.084927 Y61.093519 Z4 E14145.740369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X157.012846 Y59.962846 Z4 E14149.077436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X157.041689 Y59.939175 Z4 E14149.17032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X158.167555 Y59.015202 Z4 E14153.097474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X158.205946 Y58.994681 Z4 E14153.223899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X159.484952 Y58.311038 Z4 E14157.735979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X159.53256 Y58.296596 Z4 E14157.901106 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X160.914412 Y57.877416 Z4 E14162.992951 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X160.970111 Y57.87193 Z4 E14163.20194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X162.401 Y57.731 Z4 E14168.86839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X162.462888 Y57.737095 Z4 E14169.126401 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=prime ramp
G1 X163.887588 Y57.877416 Z4 E14175.078275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034
G1 X164.700635 Y58.124051 Z4 E14178.610632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034
G1 X165.317048 Y58.311038 Z4.322075 E14181.604798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=4 matz1=4.322075 note=collision lift
G1 X166.634445 Y59.015202 Z5.068966 E14188.54826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=4.322075 matz1=5.068966 note=collision lift
G1 X167.789154 Y59.962846 Z5.815856 E14195.491721 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=5.068966 matz1=5.815856 note=collision lift
G1 X168.736798 Y61.117555 Z6.562747 E14202.435182 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=5.815856 matz1=6 note=collision lift
G1 X169.440962 Y62.434952 Z7.309637 E14209.378644 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.843596 Y63.76226 Z8 E14215.82006 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.845427 Y63.768296 Z8 E14215.846283 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.874584 Y63.864412 Z8 E14216.263867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X170.021 Y65.351 Z8 E14222.474288 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.988423 Y65.681758 Z8 E14223.856075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.988391 Y65.682087 Z8 E14223.857449 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.966404 Y65.905319 Z7.89856 E14224.880956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.966311 Y65.906265 Z7.899035 E14224.885375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.874584 Y66.837588 Z7.455069 E14229.191734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X169.440962 Y68.267048 Z6.708179 E14236.135196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=6 note=collision lift
G1 X168.736798 Y69.584445 Z5.961288 E14243.078657 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=6 matz1=5.961288 note=collision lift
G1 X167.789154 Y70.739154 Z5.214398 E14250.022118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=5.961288 matz1=5.214398 note=collision lift
G1 X166.634445 Y71.686798 Z4.467507 E14256.96558 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=5.214398 matz1=4.467507 note=collision lift
G1 X165.809837 Y72.127561 Z4 E14261.311754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 matz0=4.467507 matz1=4 note=collision lift
G1 X165.317048 Y72.390962 Z4 E14263.634838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034
G1 X163.887588 Y72.824584 Z4 E14269.845259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034
G1 X162.401 Y72.971 Z4 E14276.05568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034
G1 X160.914412 Y72.824584 Z4 E14282.2661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034
G1 X159.484952 Y72.390962 Z4 E14288.476521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034
G1 X158.624969 Y71.931291 Z4 E14292.530619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034
G1 X158.167555 Y71.686798 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=end-early tail
G1 X157.012846 Y70.739154 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=end-early tail
G1 X156.065202 Y69.584445 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=end-early tail
G1 X155.361038 Y68.267048 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0034 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0034
G0 X155.361038 Y68.267048 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0033 note=intra-page lift
G0 X142.270866 Y73.469034 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0033 note=intra-page XY
G0 X142.270866 Y73.469034 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0033 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0033
G1 X143.346565 Y72.423628 Z4 E14292.842433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X143.598822 Y72.178475 Z4 E14293.005824 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X144.470746 Y71.431342 Z4 E14293.777874 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X144.868715 Y71.09033 Z4 E14294.251719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X145.653935 Y70.510819 Z4 E14295.336943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X146.082391 Y70.194609 Z4 E14296.040411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X146.906406 Y69.687615 Z4 E14297.519639 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X147.241698 Y69.48132 Z4 E14298.195796 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X148.235692 Y68.995588 Z4 E14300.325963 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X148.348482 Y68.940471 Z4 E14300.589109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X149.404593 Y68.56207 Z4 E14303.134622 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X149.651077 Y68.50678 Z4 E14303.755914 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X150.411875 Y68.336125 Z4 E14305.785143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X151.129465 Y68.273744 Z4 E14307.809493 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X151.372177 Y68.252645 Z4 E14308.526737 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X152.287346 Y68.301639 Z4 E14311.372219 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X152.620851 Y68.36723 Z4 E14312.4867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X153.159228 Y68.473114 Z4 E14314.353376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X153.989672 Y68.757078 Z4 E14317.512677 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X154.05585 Y68.789417 Z4 E14317.787534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X154.780524 Y69.143541 Z4 E14320.895685 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X155.365643 Y69.515671 Z4 E14323.711996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=prime ramp
G1 X155.533631 Y69.62251 Z4 E14324.539691 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X156.934 Y70.818 Z4 E14332.194752 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X158.12949 Y72.218369 Z4 E14339.849813 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X158.608459 Y72.971476 Z4 E14343.560456 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X158.994922 Y73.762328 Z4 E14347.220015 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X159.278886 Y74.592772 Z4 E14350.868867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X159.450361 Y75.464654 Z4 E14354.563173 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X159.499355 Y76.379823 Z4 E14358.373451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X159.415875 Y77.340125 Z4 E14362.38098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X159.18993 Y78.347407 Z4 E14366.672836 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X158.811529 Y79.403518 Z4 E14371.336962 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X158.27068 Y80.510302 Z4 E14376.458461 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X157.557391 Y81.669609 Z4 E14382.117533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X156.66167 Y82.883285 Z4 E14388.388807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X155.573525 Y84.153178 Z4 E14395.341544 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X154.282966 Y85.481134 Z4 E14403.040262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X152.78 Y86.869 Z4 E14411.545489 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X151.566027 Y88.399059 Z4 E14419.665758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X149.578781 Y90.466094 Z4 E14431.586876 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X146.851145 Y92.89777 Z4 E14446.779201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X143.416 Y95.52175 Z4 E14464.750782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X141.443388 Y96.852 Z4 E14474.642493 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X139.30623 Y98.165699 Z4 E14485.072186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X137.008637 Y99.441307 Z4 E14495.997924 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X134.554719 Y100.657281 Z4 E14507.383987 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X131.948585 Y101.79208 Z4 E14519.20165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X129.194348 Y102.82416 Z4 E14531.429992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X126.296116 Y103.731981 Z4 E14544.056725 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X123.258 Y104.494 Z4 E14557.078995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X124.020019 Y101.455884 Z4 E14570.101264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X124.92784 Y98.557652 Z4 E14582.727997 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X125.95992 Y95.803415 Z4 E14594.956339 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X127.094719 Y93.197281 Z4 E14606.774002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X128.310693 Y90.743363 Z4 E14618.160065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X129.586301 Y88.44577 Z4 E14629.085803 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X130.9 Y86.308612 Z4 E14639.515496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X132.23025 Y84.336 Z4 E14649.407207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X134.85423 Y80.900855 Z4 E14667.378788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X137.285906 Y78.173219 Z4 E14682.571113 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X138.631266 Y76.879791 Z4 E14690.330143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033
G1 X139.352941 Y76.185973 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=end-early tail
G1 X140.883 Y74.972 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=end-early tail
G1 X142.270866 Y73.469034 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0033 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0033
G0 X142.270866 Y73.469034 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0032 note=intra-page lift
G0 X131.905412 Y63.792416 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0032 note=intra-page XY
G0 X131.905412 Y63.792416 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0032 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0032
G1 X133.392 Y63.646 Z4 E14690.639377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X133.398189 Y63.64661 Z4 E14690.641957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X134.878588 Y63.792416 Z4 E14691.567078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X134.89049 Y63.796027 Z4 E14691.577398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X136.308048 Y64.226038 Z4 E14693.113246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X136.324501 Y64.234833 Z4 E14693.136467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X137.625445 Y64.930202 Z4 E14695.277882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X137.644674 Y64.945982 Z4 E14695.319163 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X138.780154 Y65.877846 Z4 E14698.060985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X138.799879 Y65.901882 Z4 E14698.125487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X139.727798 Y67.032555 Z4 E14701.462555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X139.745388 Y67.065462 Z4 E14701.555439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X140.431962 Y68.349952 Z4 E14705.482592 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X140.444599 Y68.391609 Z4 E14705.609018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X140.865584 Y69.779412 Z4 E14710.121097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X140.87046 Y69.828922 Z4 E14710.286224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X141.012 Y71.266 Z4 E14715.378069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X141.006514 Y71.3217 Z4 E14715.587058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X140.865584 Y72.752588 Z4 E14721.253509 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X140.847532 Y72.812098 Z4 E14721.51152 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=prime ramp
G1 X140.431962 Y74.182048 Z4 E14727.463394 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X139.727798 Y75.499445 Z4 E14733.673814 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X138.780154 Y76.654154 Z4 E14739.884235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X137.625445 Y77.601798 Z4 E14746.094655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X136.308048 Y78.305962 Z4 E14752.305076 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X134.878588 Y78.739584 Z4 E14758.515497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X133.392 Y78.886 Z4 E14764.725917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X131.905412 Y78.739584 Z4 E14770.936338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X130.475952 Y78.305962 Z4 E14777.146759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X129.158555 Y77.601798 Z4 E14783.357179 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X128.003846 Y76.654154 Z4 E14789.5676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X127.056202 Y75.499445 Z4 E14795.77802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X126.352038 Y74.182048 Z4 E14801.988441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X125.918416 Y72.752588 Z4 E14808.198862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X125.772 Y71.266 Z4 E14814.409282 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X125.918416 Y69.779412 Z4 E14820.619703 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X126.352038 Y68.349952 Z4 E14826.830124 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X127.056202 Y67.032555 Z4 E14833.040544 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X127.674814 Y66.278773 Z4 E14837.094642 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032
G1 X128.003846 Y65.877846 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=end-early tail
G1 X129.158555 Y64.930202 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=end-early tail
G1 X130.475952 Y64.226038 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=end-early tail
G1 X131.905412 Y63.792416 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0032 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0032
G0 X131.905412 Y63.792416 Z8.04532 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0031 note=intra-page lift
G0 X128.330485 Y50.852101 Z8.04532 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0031 note=intra-page XY
G0 X128.330485 Y50.852101 Z4.04532 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0031 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0031
G1 X128.09393 Y50.190975 Z4.396403 E14837.180053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.04532 matz1=4.396403 note=collision lift
G1 X128.093869 Y50.190805 Z4.396313 E14837.180096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.396403 matz1=4.396313 note=collision lift
G1 X127.97169 Y49.849337 Z4.577646 E14837.291131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.396313 matz1=4.577646 note=collision lift
G1 X127.970221 Y49.845232 Z4.58001 E14837.292771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.577646 matz1=4.58001 note=collision lift
G1 X127.904085 Y49.581203 Z4.716102 E14837.406456 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.58001 matz1=4.716102 note=collision lift
G1 X127.799607 Y49.164103 Z4.931094 E14837.638353 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.716102 matz1=4.931094 note=collision lift
G1 X127.799563 Y49.163928 Z4.931004 E14837.638463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.931094 matz1=4.931004 note=collision lift
G1 X127.712501 Y48.816356 Z5.110157 E14837.880655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.931004 matz1=5.110157 note=collision lift
G1 X127.710383 Y48.807899 Z5.114701 E14837.887158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.110157 matz1=5.114701 note=collision lift
G1 X127.630507 Y48.269419 Z5.386885 E14838.341897 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.114701 matz1=5.386885 note=collision lift
G1 X127.607353 Y48.113327 Z5.465784 E14838.492909 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.386885 matz1=5.465784 note=collision lift
G1 X127.607326 Y48.113148 Z5.465694 E14838.493087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.465784 matz1=5.465694 note=collision lift
G1 X127.555391 Y47.763027 Z5.642669 E14838.863214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.465694 matz1=5.642669 note=collision lift
G1 X127.553472 Y47.750093 Z5.649391 E14838.877801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.642669 matz1=5.649391 note=collision lift
G1 X127.519018 Y47.048766 Z6.000475 E14839.743723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.649391 matz1=6 note=collision lift
G1 X127.518971 Y47.047817 Z6 E14839.74501 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X127.512748 Y46.921143 Z6 E14839.900966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X127.501 Y46.682 Z6 E14840.207543 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X127.553472 Y45.613907 Z6 E14841.770782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X127.581525 Y45.424789 Z6 E14842.083663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X127.710383 Y44.556101 Z6 E14843.650983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X127.861469 Y43.952929 Z6 E14844.889987 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X127.970221 Y43.518768 Z6 E14845.848147 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X128.324773 Y42.527863 Z6 E14848.319938 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X128.330485 Y42.511899 Z6 E14848.362273 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X128.787704 Y41.54519 Z6 E14851.193361 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X128.975999 Y41.231039 Z6 E14852.235867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X128.976487 Y41.230225 Z6.000475 E14852.238943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X128.997797 Y41.194671 Z5.979749 E14852.373517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=5.979303 note=collision lift
G1 X129.337476 Y40.627951 Z5.649391 E14854.598975 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.979303 matz1=5.649391 note=collision lift
G1 X129.743099 Y40.081031 Z5.308931 E14857.050723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.649391 matz1=5.308931 note=collision lift
G1 X129.974449 Y39.769092 Z5.114747 E14858.521032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.308931 matz1=5.114747 note=collision lift
G1 X129.974505 Y39.769016 Z5.114701 E14858.521393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X130.614622 Y39.062757 Z4.638111 E14862.351557 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.114701 matz1=4.638111 note=collision lift
G1 X130.692657 Y38.976657 Z4.58001 E14862.840014 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.638111 matz1=4.58001 note=collision lift
G1 X131.485016 Y38.258505 Z4.04532 E14867.554837 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X131.557819 Y38.204511 Z4 E14867.972674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.04532 matz1=4 note=collision lift
G1 X131.616566 Y38.160941 Z4 E14868.276019 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 note=prime ramp
G1 X132.343951 Y37.621476 Z4 E14872.041067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X133.26119 Y37.071704 Z4 E14876.487036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X134.227899 Y36.614485 Z4 E14880.933005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X135.234768 Y36.254221 Z4 E14885.378974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X136.272101 Y35.994383 Z4 E14889.824943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X137.329907 Y35.837472 Z4 E14894.270912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X138.398 Y35.785 Z4 E14898.716882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X139.466093 Y35.837472 Z4 E14903.162851 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X140.523899 Y35.994383 Z4 E14907.60882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X141.561232 Y36.254221 Z4 E14912.054789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X142.568101 Y36.614485 Z4 E14916.500758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X142.917425 Y36.779702 Z4 E14918.107324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X143.53481 Y37.071704 Z4.341478 E14921.281873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4 matz1=4.341478 note=collision lift
G1 X144.452049 Y37.621476 Z4.876169 E14926.252618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X145.310984 Y38.258505 Z5.410859 E14931.223362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X146.103343 Y38.976657 Z5.94555 E14936.194107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X146.821495 Y39.769016 Z6.48024 E14941.164852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.94555 matz1=6 note=collision lift
G1 X147.458524 Y40.627951 Z7.014931 E14946.135596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X148.008296 Y41.54519 Z7.549621 E14951.106341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X148.39342 Y42.359465 Z8 E14955.293285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X148.465515 Y42.511899 Z8 E14955.994337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X148.825779 Y43.518768 Z8 E14960.440306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.085617 Y44.556101 Z8 E14964.886276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.242528 Y45.613907 Z8 E14969.332245 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.295 Y46.682 Z8 E14973.778214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.242528 Y47.750093 Z8 E14978.224183 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.167188 Y48.257994 Z8 E14980.358895 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.167008 Y48.259205 Z8 E14980.363984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.085617 Y48.807899 Z7.737636 E14982.915106 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.082551 Y48.82014 Z7.731326 E14982.973763 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.041171 Y48.985339 Z7.652265 E14983.754377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X149.039746 Y48.991027 Z7.655196 E14983.781632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X148.825779 Y49.845232 Z7.220833 E14987.863882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X148.465515 Y50.852101 Z6.686142 E14992.834627 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X148.008296 Y51.81881 Z6.151452 E14997.805371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=6 note=collision lift
G1 X147.458524 Y52.736049 Z5.616761 E15002.776116 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=5.616761 note=collision lift
G1 X146.821495 Y53.594984 Z5.082071 E15007.74686 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X146.103343 Y54.387343 Z4.547381 E15012.717605 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X145.310984 Y55.105495 Z4.01269 E15017.68835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X145.290598 Y55.120614 Z4 E15017.806323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.01269 matz1=4 note=collision lift
G1 X144.452049 Y55.742524 Z4 E15022.146773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X143.53481 Y56.292296 Z4 E15026.592742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X142.568101 Y56.749515 Z4 E15031.038712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X141.561232 Y57.109779 Z4 E15035.484681 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X140.523899 Y57.369617 Z4 E15039.93065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X139.466093 Y57.526528 Z4 E15044.376619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X138.398 Y57.579 Z4 E15048.822588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X137.329907 Y57.526528 Z4 E15053.268557 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X136.272101 Y57.369617 Z4 E15057.714526 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X135.234768 Y57.109779 Z4 E15062.160495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X134.227899 Y56.749515 Z4 E15066.606465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X133.26119 Y56.292296 Z4 E15071.052434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X132.343951 Y55.742524 Z4 E15075.498403 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X131.485016 Y55.105495 Z4 E15079.944372 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X131.481022 Y55.101875 Z4 E15079.966785 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031
G1 X130.843908 Y54.524428 Z4.42993 E15083.963625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4 matz1=4.42993 note=collision lift
G1 X130.692657 Y54.387343 Z4.531995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.42993 matz1=4.531995 note=collision lift
G1 X129.974505 Y53.594984 Z5.066685 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=4.531995 matz1=5.066685 note=collision lift
G1 X129.337476 Y52.736049 Z5.601376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.066685 matz1=5.601376 note=collision lift
G1 X128.880945 Y51.974373 Z6.045383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.601376 matz1=6 note=collision lift
G1 X128.787704 Y51.81881 Z5.9547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=6 matz1=5.9547 note=collision lift
G1 X128.369031 Y50.9336 Z5.465087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.9547 matz1=5.465087 note=collision lift
G1 X128.369015 Y50.933568 Z5.465087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.465087 matz1=5.465087 note=collision lift
G1 X128.330485 Y50.852101 Z5.46487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0031 matz0=5.465087 matz1=5.46487 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0031
G0 X128.330485 Y50.852101 Z9.46487 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0030 note=intra-page lift
G0 X112.891899 Y56.749515 Z9.46487 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0030 note=intra-page XY
G0 X112.891899 Y56.749515 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0030 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0030
G1 X111.92519 Y56.292296 Z4 E15084.122106 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X111.555835 Y56.070914 Z4 E15084.275439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X111.007951 Y55.742524 Z4 E15084.59755 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X110.316198 Y55.229485 Z4 E15085.21088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X110.149016 Y55.105495 Z4 E15085.389955 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X109.356657 Y54.387343 Z4 E15086.499323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X109.207251 Y54.222498 Z4 E15086.769949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X108.638505 Y53.594984 Z4 E15087.925654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X108.249457 Y53.070412 Z4 E15088.952645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X108.001476 Y52.736049 Z4 E15089.668946 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X107.451704 Y51.81881 Z4 E15091.729201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X107.445576 Y51.805853 Z4 E15091.758969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X107.033238 Y50.934038 Z4 E15093.892634 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=prime ramp
G1 X106.994485 Y50.852101 Z4.04532 E15094.131802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4 matz1=4.04532 note=collision lift
G1 X106.863634 Y50.486397 Z4.239524 E15095.188921 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.04532 matz1=4.239524 note=collision lift
G1 X106.634221 Y49.845232 Z4.58001 E15097.168446 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.239524 matz1=4.58001 note=collision lift
G1 X106.473692 Y49.204363 Z4.910345 E15099.242499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.58001 matz1=4.910345 note=collision lift
G1 X106.374383 Y48.807899 Z5.114701 E15100.601293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.910345 matz1=5.114701 note=collision lift
G1 X106.374369 Y48.807807 Z5.114747 E15100.601611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X106.237494 Y47.885068 Z5.581165 E15103.919706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.114747 matz1=5.581165 note=collision lift
G1 X106.217472 Y47.750093 Z5.649391 E15104.430342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.581165 matz1=5.649391 note=collision lift
G1 X106.183018 Y47.048766 Z6.000475 E15107.16004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.649391 matz1=6 note=collision lift
G1 X106.182971 Y47.047817 Z6 E15107.163847 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X106.165 Y46.682 Z6 E15108.495908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X106.174572 Y46.487165 Z6 E15109.22054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X106.217472 Y45.613907 Z6 E15112.597944 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X106.30928 Y44.994991 Z6 E15115.145002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X106.374383 Y44.556101 Z6 E15116.989659 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X106.634221 Y43.518768 Z6 E15121.435628 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X106.994485 Y42.511899 Z6 E15125.881597 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X107.451704 Y41.54519 Z6 E15130.327566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X107.639999 Y41.231039 Z6 E15131.850293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X107.640487 Y41.230225 Z6.000475 E15131.854707 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X108.001476 Y40.627951 Z5.649391 E15135.118573 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=5.649391 note=collision lift
G1 X108.638449 Y39.769092 Z5.114747 E15140.088882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X108.638505 Y39.769016 Z5.114701 E15140.089317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X109.356657 Y38.976657 Z4.58001 E15145.060062 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X110.149016 Y38.258505 Z4.04532 E15150.030806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X110.221819 Y38.204511 Z4 E15150.45212 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.04532 matz1=4 note=collision lift
G1 X111.007951 Y37.621476 Z4 E15154.521255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X111.92519 Y37.071704 Z4 E15158.967224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X112.891899 Y36.614485 Z4 E15163.413193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X113.898768 Y36.254221 Z4 E15167.859162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X114.936101 Y35.994383 Z4 E15172.305131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X115.993907 Y35.837472 Z4 E15176.7511 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X117.062 Y35.785 Z4 E15181.197069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X118.130093 Y35.837472 Z4 E15185.643039 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X119.187899 Y35.994383 Z4 E15190.089008 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X120.225232 Y36.254221 Z4 E15194.534977 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X121.232101 Y36.614485 Z4 E15198.980946 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X121.581425 Y36.779702 Z4 E15200.587512 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X122.19881 Y37.071704 Z4.341478 E15203.762061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4 matz1=4.341478 note=collision lift
G1 X123.116049 Y37.621476 Z4.876169 E15208.732806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X123.974984 Y38.258505 Z5.410859 E15213.70355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X124.767343 Y38.976657 Z5.94555 E15218.674295 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X125.485495 Y39.769016 Z6.48024 E15223.64504 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.94555 matz1=6 note=collision lift
G1 X126.122524 Y40.627951 Z7.014931 E15228.615784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X126.672296 Y41.54519 Z7.549621 E15233.586529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.05742 Y42.359465 Z8 E15237.773473 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.129515 Y42.511899 Z8 E15238.474525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.489779 Y43.518768 Z8 E15242.920494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.749617 Y44.556101 Z8 E15247.366464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.906528 Y45.613907 Z8 E15251.812433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.959 Y46.682 Z8 E15256.258402 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.906528 Y47.750093 Z8 E15260.704371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.831188 Y48.257994 Z8 E15262.839083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.831008 Y48.259205 Z8 E15262.844172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.749617 Y48.807899 Z7.737636 E15265.395294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.746551 Y48.82014 Z7.731326 E15265.453951 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.703746 Y48.991027 Z7.649543 E15266.261441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.701858 Y48.998566 Z7.645657 E15266.297565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.700597 Y49.003598 Z7.643163 E15266.321495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.700348 Y49.004593 Z7.643676 E15266.326265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.610758 Y49.362255 Z7.467151 E15268.02582 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.610491 Y49.363323 Z7.467701 E15268.030933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.533413 Y49.671035 Z7.309092 E15269.505443 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.489779 Y49.845232 Z7.398881 E15270.340172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.445312 Y49.969509 Z7.464878 E15270.953707 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.372235 Y50.173744 Z7.465085 E15271.855535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.368415 Y50.184421 Z7.470754 E15271.908243 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.244343 Y50.53118 Z7.510268 E15273.448194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.24105 Y50.540383 Z7.505381 E15273.493629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.187635 Y50.689667 Z7.502615 E15274.152911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.186929 Y50.691641 Z7.503663 E15274.162656 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.129515 Y50.852101 Z7.477489 E15274.8795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.118913 Y50.874519 Z7.46509 E15274.99477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X127.084167 Y50.947981 Z7.464886 E15275.332631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X126.672296 Y51.81881 Z6.983227 E15279.810367 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X126.122524 Y52.736049 Z6.448537 E15284.781112 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=6 note=collision lift
G1 X125.485495 Y53.594984 Z5.913847 E15289.751856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=6 matz1=5.913847 note=collision lift
G1 X124.767343 Y54.387343 Z5.379156 E15294.722601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.913847 matz1=5.379156 note=collision lift
G1 X123.974984 Y55.105495 Z4.844466 E15299.693345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=5.379156 matz1=4.844466 note=collision lift
G1 X123.116049 Y55.742524 Z4.309775 E15304.66409 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.844466 matz1=4.309775 note=collision lift
G1 X122.584643 Y56.061037 Z4 E15307.543912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 matz0=4.309775 matz1=4 note=collision lift
G1 X122.19881 Y56.292296 Z4 E15309.41409 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X121.232101 Y56.749515 Z4 E15313.860059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X120.225232 Y57.109779 Z4 E15318.306028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X119.187899 Y57.369617 Z4 E15322.751997 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X118.130093 Y57.526528 Z4 E15327.197967 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X117.783606 Y57.54355 Z4 E15328.640228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030
G1 X117.062 Y57.579 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=end-early tail
G1 X115.993907 Y57.526528 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=end-early tail
G1 X114.936101 Y57.369617 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=end-early tail
G1 X113.898768 Y57.109779 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=end-early tail
G1 X112.891899 Y56.749515 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0030 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0030
G0 X112.891899 Y56.749515 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0029 note=intra-page lift
G0 X108.713804 Y65.944732 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0029 note=intra-page XY
G0 X108.713804 Y65.944732 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0029 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0029
G1 X108.723531 Y65.82761 Z4 E15328.642142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X108.945181 Y64.46302 Z4 E15328.952041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X108.948359 Y64.443453 Z4 E15328.960337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X109.263744 Y63.214669 Z4 E15329.717769 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X109.337182 Y63.016259 Z4 E15329.887483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X109.663924 Y62.13349 Z4 E15330.792966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X109.917391 Y61.635592 Z4 E15331.446552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X110.143138 Y61.192148 Z4 E15332.101498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X110.695625 Y60.382875 Z4 E15333.591865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X110.710738 Y60.366178 Z4 E15333.629248 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X111.315624 Y59.697903 Z4 E15335.240838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X111.775395 Y59.314547 Z4 E15336.435572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X111.997373 Y59.129463 Z4 E15337.047943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X112.735112 Y58.669788 Z4 E15339.029199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X113.046157 Y58.528201 Z4 E15339.865523 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X113.523078 Y58.311109 Z4 E15341.210714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X114.355511 Y58.045659 Z4 E15343.622945 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X114.455657 Y58.024968 Z4 E15343.919102 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X115.22665 Y57.86567 Z4 E15346.296181 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X115.937462 Y57.813514 Z4 E15348.596309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X117.062 Y57.731 Z4 E15352.522788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X117.43344 Y57.758255 Z4 E15353.897143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X118.89735 Y57.86567 Z4 E15359.688063 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X118.928839 Y57.872176 Z4 E15359.821604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=prime ramp
G1 X119.768489 Y58.045659 Z4 E15363.386192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X120.600922 Y58.311109 Z4 E15367.018751 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X121.388888 Y58.669788 Z4 E15370.618165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X122.126627 Y59.129463 Z4 E15374.232 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X122.808376 Y59.697903 Z4 E15377.922381 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X123.428375 Y60.382875 Z4 E15381.763498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X123.980862 Y61.192148 Z4 E15385.837366 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X124.460076 Y62.13349 Z4 E15390.228954 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X124.860256 Y63.214669 Z4 E15395.021999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X125.175641 Y64.443453 Z4 E15400.296277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X125.400469 Y65.82761 Z4 E15406.126352 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X125.528979 Y67.374908 Z4 E15412.581419 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X125.555409 Y69.093115 Z4 E15419.72574 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X125.474 Y70.99 Z4 E15427.619329 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X125.697758 Y72.79043 Z4 E15435.162232 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X125.754313 Y75.450688 Z4 E15446.224798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X125.545086 Y78.836102 Z4 E15460.326568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X124.9715 Y82.812 Z4 E15477.027562 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X124.517267 Y84.979296 Z4 E15486.233903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X123.934977 Y87.243711 Z4 E15495.954527 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X123.212308 Y89.588411 Z4 E15506.15517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X122.336938 Y91.996563 Z4 E15516.808045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X121.296544 Y94.451331 Z4 E15527.89257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X120.078805 Y96.935883 Z4 E15539.396117 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X118.671397 Y99.433384 Z4 E15551.314715 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X117.062 Y101.927 Z4 E15563.653706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X115.452603 Y99.433384 Z4 E15575.992696 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X114.045195 Y96.935883 Z4 E15587.911294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X112.827456 Y94.451331 Z4 E15599.414841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X111.787063 Y91.996563 Z4 E15610.499367 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X110.911692 Y89.588411 Z4 E15621.152241 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X110.189023 Y87.243711 Z4 E15631.352884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X109.606733 Y84.979296 Z4 E15641.073508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X109.1525 Y82.812 Z4 E15650.27985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X108.578914 Y78.836102 Z4 E15666.980844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X108.369688 Y75.450688 Z4 E15681.082614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X108.426242 Y72.79043 Z4 E15692.14518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X108.65 Y70.99 Z4 E15699.688083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X108.647764 Y70.937907 Z4 E15699.90486 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029
G1 X108.568591 Y69.093115 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=end-early tail
G1 X108.595021 Y67.374908 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=end-early tail
G1 X108.713804 Y65.944732 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0029 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0029
G0 X108.713804 Y65.944732 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0028 note=intra-page lift
G0 X96.498555 Y64.930202 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0028 note=intra-page XY
G0 X96.498555 Y64.930202 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0028 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0028
G1 X97.815952 Y64.226038 Z4 E15700.214094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X97.821903 Y64.224233 Z4 E15700.216674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X99.245412 Y63.792416 Z4 E15701.141795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X99.257789 Y63.791197 Z4 E15701.152116 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X100.732 Y63.646 Z4 E15702.687963 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X100.750567 Y63.647829 Z4 E15702.711184 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X102.218588 Y63.792416 Z4 E15704.852599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X102.242392 Y63.799637 Z4 E15704.893881 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X103.648048 Y64.226038 Z4 E15707.635702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X103.67547 Y64.240696 Z4 E15707.700205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X104.965445 Y64.930202 Z4 E15711.037272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X104.994288 Y64.953872 Z4 E15711.130156 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X106.120154 Y65.877846 Z4 E15715.05731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X106.14777 Y65.911497 Z4 E15715.183735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X107.067798 Y67.032555 Z4 E15719.695815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X107.091251 Y67.076431 Z4 E15719.860942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X107.771962 Y68.349952 Z4 E15724.952787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X107.788209 Y68.403511 Z4 E15725.161776 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X108.205584 Y69.779412 Z4 E15730.828226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X108.211679 Y69.8413 Z4 E15731.086237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=prime ramp
G1 X108.352 Y71.266 Z4 E15737.038111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X108.205584 Y72.752588 Z4 E15743.248531 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X107.771962 Y74.182048 Z4 E15749.458952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X107.067798 Y75.499445 Z4 E15755.669373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X106.120154 Y76.654154 Z4 E15761.879793 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X104.965445 Y77.601798 Z4 E15768.090214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X103.648048 Y78.305962 Z4 E15774.300635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X102.218588 Y78.739584 Z4 E15780.511055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X100.732 Y78.886 Z4 E15786.721476 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X99.245412 Y78.739584 Z4 E15792.931897 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X97.815952 Y78.305962 Z4 E15799.142317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X96.498555 Y77.601798 Z4 E15805.352738 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X95.343846 Y76.654154 Z4 E15811.563158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X94.396202 Y75.499445 Z4 E15817.773579 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X93.692038 Y74.182048 Z4 E15823.984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X93.258416 Y72.752588 Z4 E15830.19442 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X93.112 Y71.266 Z4 E15836.404841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X93.258416 Y69.779412 Z4 E15842.615262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X93.54148 Y68.846275 Z4 E15846.66936 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028
G1 X93.692038 Y68.349952 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=end-early tail
G1 X94.396202 Y67.032555 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=end-early tail
G1 X95.343846 Y65.877846 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=end-early tail
G1 X96.498555 Y64.930202 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0028 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0028
G0 X96.498555 Y64.930202 Z9.128864 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0027 note=intra-page lift
G0 X85.034237 Y48.779949 Z9.128864 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0027 note=intra-page XY
G0 X85.034237 Y48.779949 Z5.128864 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0027 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0027
G1 X84.935353 Y48.113327 Z5.465747 E15846.748027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.128864 matz1=5.465747 note=collision lift
G1 X84.935332 Y48.113185 Z5.465675 E15846.748061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.465747 matz1=5.465675 note=collision lift
G1 X84.881497 Y47.750261 Z5.649121 E15846.857058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.465675 matz1=5.649121 note=collision lift
G1 X84.881472 Y47.750093 Z5.649391 E15846.857161 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.649121 matz1=5.649391 note=collision lift
G1 X84.866731 Y47.450023 Z5.799606 E15846.981173 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.649391 matz1=5.799403 note=collision lift
G1 X84.847018 Y47.048766 Z6.000475 E15847.195871 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.799403 matz1=6 note=collision lift
G1 X84.846971 Y47.047817 Z6 E15847.196444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X84.829 Y46.682 Z6 E15847.413011 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X84.862539 Y45.999303 Z6 E15847.916615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X84.881472 Y45.613907 Z6 E15848.258092 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.038383 Y44.556101 Z6 E15849.420135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.049258 Y44.512683 Z6 E15849.475684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.298221 Y43.518768 Z6 E15850.899141 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.458371 Y43.071178 Z6 E15851.65838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.658485 Y42.511899 Z6 E15852.695109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X86.045848 Y41.692887 Z6 E15854.464704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X86.115704 Y41.54519 Z6 E15854.808039 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X86.303999 Y41.231039 Z6 E15855.604578 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X86.304487 Y41.230225 Z6.000475 E15855.606941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X86.665476 Y40.627951 Z5.649391 E15857.439761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=5.649391 note=collision lift
G1 X86.763643 Y40.495588 Z5.566995 E15857.894655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.649391 matz1=5.566995 note=collision lift
G1 X87.302449 Y39.769092 Z5.114747 E15860.558963 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.566995 matz1=5.114747 note=collision lift
G1 X87.302505 Y39.769016 Z5.114701 E15860.559253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X87.596012 Y39.445182 Z4.896174 E15861.948234 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.114701 matz1=4.896174 note=collision lift
G1 X88.020657 Y38.976657 Z4.58001 E15864.074949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.896174 matz1=4.58001 note=collision lift
G1 X88.546224 Y38.500312 Z4.225354 E15866.625441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.58001 matz1=4.225354 note=collision lift
G1 X88.813016 Y38.258505 Z4.04532 E15867.986848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.225354 matz1=4.04532 note=collision lift
G1 X88.885819 Y38.204511 Z4 E15868.336629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.04532 matz1=4 note=collision lift
G1 X89.671951 Y37.621476 Z4 E15871.861389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 note=prime ramp
G1 X89.686835 Y37.612555 Z4 E15871.926275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 note=prime ramp
G1 X90.58919 Y37.071704 Z4 E15876.016099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 note=prime ramp
G1 X90.994151 Y36.880172 Z4 E15877.850736 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 note=prime ramp
G1 X91.555899 Y36.614485 Z4 E15880.434257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X92.562768 Y36.254221 Z4 E15884.880226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X93.600101 Y35.994383 Z4 E15889.326195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X94.657907 Y35.837472 Z4 E15893.772164 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X95.726 Y35.785 Z4 E15898.218134 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X96.794093 Y35.837472 Z4 E15902.664103 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X97.851899 Y35.994383 Z4 E15907.110072 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X98.889232 Y36.254221 Z4 E15911.556041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X99.896101 Y36.614485 Z4 E15916.00201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X100.245425 Y36.779702 Z4 E15917.608576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X100.86281 Y37.071704 Z4.341478 E15920.783125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4 matz1=4.341478 note=collision lift
G1 X101.780049 Y37.621476 Z4.876169 E15925.75387 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X102.638984 Y38.258505 Z5.410859 E15930.724614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X103.431343 Y38.976657 Z5.94555 E15935.695359 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X104.149495 Y39.769016 Z6.48024 E15940.666104 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.94555 matz1=6 note=collision lift
G1 X104.786524 Y40.627951 Z7.014931 E15945.636848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X105.336296 Y41.54519 Z7.549621 E15950.607593 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X105.72142 Y42.359465 Z8 E15954.794537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X105.793515 Y42.511899 Z8 E15955.495589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.153779 Y43.518768 Z8 E15959.941559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.413617 Y44.556101 Z8 E15964.387528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.570528 Y45.613907 Z8 E15968.833497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.623 Y46.682 Z8 E15973.279466 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.570528 Y47.750093 Z8 E15977.725435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.495188 Y48.257994 Z8 E15979.860147 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.495008 Y48.259205 Z8 E15979.865237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.413617 Y48.807899 Z7.737636 E15982.416358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.410551 Y48.82014 Z7.731326 E15982.475015 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.369171 Y48.985339 Z7.652265 E15983.255629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.367746 Y48.991027 Z7.655196 E15983.282884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X106.153779 Y49.845232 Z7.220833 E15987.365134 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X105.793515 Y50.852101 Z6.686142 E15992.335879 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X105.336296 Y51.81881 Z6.151452 E15997.306623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X104.786524 Y52.736049 Z5.616761 E16002.277368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=5.616761 note=collision lift
G1 X104.149495 Y53.594984 Z5.082071 E16007.248112 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X103.431343 Y54.387343 Z4.547381 E16012.218857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X102.638984 Y55.105495 Z4.01269 E16017.189602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X102.618598 Y55.120614 Z4 E16017.307575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.01269 matz1=4 note=collision lift
G1 X101.780049 Y55.742524 Z4 E16021.648025 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X100.86281 Y56.292296 Z4 E16026.093995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X99.896101 Y56.749515 Z4 E16030.539964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X98.889232 Y57.109779 Z4 E16034.985933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X97.851899 Y57.369617 Z4 E16039.431902 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X96.794093 Y57.526528 Z4 E16043.877871 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X95.726 Y57.579 Z4 E16048.32384 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X94.657907 Y57.526528 Z4 E16052.769809 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X93.600101 Y57.369617 Z4 E16057.215778 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X92.562768 Y57.109779 Z4 E16061.661747 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X91.555899 Y56.749515 Z4 E16066.107717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X90.58919 Y56.292296 Z4 E16070.553686 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X89.671951 Y55.742524 Z4 E16074.999655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X88.813016 Y55.105495 Z4 E16079.445624 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X88.063076 Y54.425788 Z4 E16083.653581 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027
G1 X88.020657 Y54.387343 Z4.028624 E16083.919687 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4 matz1=4.028624 note=collision lift
G1 X87.302505 Y53.594984 Z4.563315 E16088.890431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.028624 matz1=4.563315 note=collision lift
G1 X86.684262 Y52.76138 Z5.082237 E16093.714584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=4.563315 matz1=5.082237 note=collision lift
G1 X86.665476 Y52.736049 Z5.098005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.082237 matz1=5.098005 note=collision lift
G1 X86.115704 Y51.81881 Z5.632696 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.098005 matz1=5.632696 note=collision lift
G1 X85.697238 Y50.934038 Z6.122066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=5.632696 matz1=6 note=collision lift
G1 X85.658485 Y50.852101 Z6.212706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.349825 Y49.989455 Z7.12891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.298221 Y49.845232 Z7.12891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.127607 Y49.164103 Z7.128907 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.127563 Y49.163928 Z7.128727 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.038383 Y48.807899 Z7.128725 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.038351 Y48.807684 Z7.128507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
G1 X85.034237 Y48.779949 Z7.128507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0027 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0027
G0 X85.034237 Y48.779949 Z11.128507 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0026 note=intra-page lift
G0 X62.480484 Y52.125483 Z11.128507 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0026 note=intra-page XY
G0 X62.480484 Y52.125483 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0026 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0026
G1 X62.475515 Y52.133772 Z6 E16093.714597 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X62.475513 Y52.133775 Z6.000761 E16093.714599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X62.474731 Y52.13508 Z6 E16093.714604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X62.114524 Y52.736049 Z6 E16093.784992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X61.645577 Y53.368352 Z6 E16094.026398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X61.477495 Y53.594984 Z6 E16094.154739 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X60.759343 Y54.387343 Z6 E16094.841448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X60.649341 Y54.487043 Z6 E16094.961839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X60.086948 Y54.996766 Z6 E16095.672801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X60.086913 Y54.996798 Z6.000025 E16095.672857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X59.966984 Y55.105495 Z5.919096 E16095.865939 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=5.919096 note=collision lift
G1 X59.795883 Y55.232392 Z5.812586 E16096.133888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.919096 matz1=5.812586 note=collision lift
G1 X59.672184 Y55.324133 Z5.735612 E16096.337381 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.812586 matz1=5.735612 note=collision lift
G1 X59.672039 Y55.324241 Z5.735702 E16096.337624 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.735612 matz1=5.735702 note=collision lift
G1 X59.564687 Y55.403859 Z5.668875 E16096.520908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.735702 matz1=5.668875 note=collision lift
G1 X59.108049 Y55.742524 Z5.384619 E16097.369679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.668875 matz1=5.384619 note=collision lift
G1 X58.444918 Y56.139989 Z4.998057 E16098.703604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.384619 matz1=4.998057 note=collision lift
G1 X58.19081 Y56.292296 Z4.849928 E16099.269638 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.998057 matz1=4.849928 note=collision lift
G1 X57.245794 Y56.739255 Z4.327236 E16101.509928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.849928 matz1=4.327236 note=collision lift
G1 X57.224101 Y56.749515 Z4.315238 E16101.5658 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.327236 matz1=4.315238 note=collision lift
G1 X56.969962 Y56.840448 Z4.180279 E16102.207987 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.315238 matz1=4.180279 note=collision lift
G1 X56.217232 Y57.109779 Z4.58001 E16104.258165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.180279 matz1=4.58001 note=collision lift
G1 X55.976409 Y57.170102 Z4.704142 E16104.93988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.58001 matz1=4.704142 note=collision lift
G1 X55.179899 Y57.369617 Z5.114701 E16107.346732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.704142 matz1=5.114701 note=collision lift
G1 X55.179807 Y57.369631 Z5.114747 E16107.34702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X54.66501 Y57.445994 Z5.374962 E16108.993458 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.114747 matz1=5.374962 note=collision lift
G1 X54.122093 Y57.526528 Z5.649391 E16110.831502 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.374962 matz1=5.649391 note=collision lift
G1 X53.420766 Y57.560982 Z6.000475 E16113.335142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.649391 matz1=6 note=collision lift
G1 X53.419817 Y57.561029 Z6 E16113.338643 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X53.319694 Y57.565947 Z6 E16113.670665 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y57.579 Z6 E16114.565238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y57.526528 Z6 E16118.359341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X51.823084 Y57.502375 Z6 E16118.971499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y57.369617 Z6 E16122.470406 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X50.350715 Y57.22499 Z6 E16124.895961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y57.109779 Z6 E16126.867276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y56.749515 Z6 E16131.313245 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y56.292296 Z6 E16135.759214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X47.603039 Y56.104001 Z6 E16137.28194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X47.602225 Y56.103513 Z6.000475 E16137.286354 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X46.999951 Y55.742524 Z5.649391 E16140.55022 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=5.649391 note=collision lift
G1 X46.141092 Y55.105551 Z5.114747 E16145.52053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X46.141016 Y55.105495 Z5.114701 E16145.520965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X45.348657 Y54.387343 Z4.58001 E16150.491709 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X44.630505 Y53.594984 Z4.04532 E16155.462454 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X44.576511 Y53.522181 Z4 E16155.883768 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.04532 matz1=4 note=collision lift
G1 X43.993476 Y52.736049 Z4 E16159.952902 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X43.443704 Y51.81881 Z4 E16164.398871 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.986485 Y50.852101 Z4 E16168.844841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.626221 Y49.845232 Z4 E16173.29081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.366383 Y48.807899 Z4 E16177.736779 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.209472 Y47.750093 Z4 E16182.182748 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.157 Y46.682 Z4 E16186.628717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.209472 Y45.613907 Z4 E16191.074686 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.366383 Y44.556101 Z4 E16195.520655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.626221 Y43.518768 Z4 E16199.966624 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X42.986485 Y42.511899 Z4 E16204.412594 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X43.443704 Y41.54519 Z4 E16208.858563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X43.993476 Y40.627951 Z4 E16213.304532 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X44.630505 Y39.769016 Z4 E16217.750501 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X45.348657 Y38.976657 Z4 E16222.19647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X46.141016 Y38.258505 Z4 E16226.642439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X46.999951 Y37.621476 Z4 E16231.088408 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X47.91719 Y37.071704 Z4 E16235.534377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X48.883899 Y36.614485 Z4 E16239.980347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X49.890768 Y36.254221 Z4 E16244.426316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X50.928101 Y35.994383 Z4 E16248.872285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X51.985907 Y35.837472 Z4 E16253.318254 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X53.054 Y35.785 Z4 E16257.764223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X54.122093 Y35.837472 Z4 E16262.210192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X55.179899 Y35.994383 Z4 E16266.656161 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X56.217232 Y36.254221 Z4 E16271.10213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X57.224101 Y36.614485 Z4 E16275.548099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X58.19081 Y37.071704 Z4 E16279.994069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X59.108049 Y37.621476 Z4 E16284.440038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X59.966984 Y38.258505 Z4 E16288.886007 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X60.759343 Y38.976657 Z4 E16293.331976 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X61.477495 Y39.769016 Z4 E16297.777945 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X62.114524 Y40.627951 Z4 E16302.223914 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X62.664296 Y41.54519 Z4 E16306.669883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X63.082762 Y42.429962 Z4 E16310.739018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026
G1 X63.121515 Y42.511899 Z4.04532 E16311.160332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4 matz1=4.04532 note=collision lift
G1 X63.481779 Y43.518768 Z4.58001 E16316.131076 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.04532 matz1=4.58001 note=collision lift
G1 X63.741617 Y44.556101 Z5.114701 E16321.101821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=4.58001 matz1=5.114701 note=collision lift
G1 X63.741631 Y44.556193 Z5.114747 E16321.102256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X63.898528 Y45.613907 Z5.649391 E16326.072566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.114747 matz1=5.649391 note=collision lift
G1 X63.932982 Y46.315234 Z6.000475 E16329.336431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=5.649391 matz1=6 note=collision lift
G1 X63.933029 Y46.316183 Z6 E16329.340845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.951 Y46.682 Z6 E16330.863572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.916434 Y47.385609 Z6 E16333.792368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.898528 Y47.750093 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.741617 Y48.807899 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.481779 Y49.845232 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.121515 Y50.852101 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.048118 Y51.007287 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.048093 Y51.007339 Z6.000029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X63.048069 Y51.007391 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X62.664296 Y51.81881 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
G1 X62.480484 Y52.125483 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0026 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0026
G0 X62.480484 Y52.125483 Z10 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0025 note=intra-page lift
G0 X70.102868 Y56.694164 Z10 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0025 note=intra-page XY
G0 X70.102868 Y56.694164 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0025 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0025
G1 X69.870575 Y56.584298 Z4 E16333.801519 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 note=prime ramp
G1 X69.25319 Y56.292296 Z4.341478 E16333.936701 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4 matz1=4.341478 note=collision lift
G1 X68.885354 Y56.071824 Z4.555902 E16334.104182 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.341478 matz1=4.555902 note=collision lift
G1 X68.335951 Y55.742524 Z4.876169 E16334.47299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.555902 matz1=4.876169 note=collision lift
G1 X67.772816 Y55.324875 Z5.226723 E16335.039623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.876169 matz1=5.226723 note=collision lift
G1 X67.477016 Y55.105495 Z5.410859 E16335.405482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.226723 matz1=5.410859 note=collision lift
G1 X66.755798 Y54.451821 Z5.897543 E16336.598692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.410859 matz1=5.897543 note=collision lift
G1 X66.684657 Y54.387343 Z5.94555 E16336.734176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.897543 matz1=5.94555 note=collision lift
G1 X65.966505 Y53.594984 Z6.48024 E16338.459073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.94555 matz1=6 note=collision lift
G1 X65.861515 Y53.453421 Z6.568364 E16338.781388 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X65.329476 Y52.736049 Z7.014931 E16340.580173 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X65.098897 Y52.351352 Z7.239184 E16341.587712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X64.779704 Y51.81881 Z7.549621 E16343.097477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X64.471536 Y51.167245 Z7.910004 E16345.017663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X64.39458 Y51.004535 Z8 E16345.525262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X64.322485 Y50.852101 Z8 E16345.959238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.962221 Y49.845232 Z8 E16348.894927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.947458 Y49.786293 Z8 E16349.071242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.702383 Y48.807899 Z8 E16352.147577 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.630283 Y48.321839 Z8 E16353.748449 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.545472 Y47.750093 Z8 E16355.71719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.500232 Y46.829205 Z8 E16359.049283 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.493 Y46.682 Z8 E16359.603765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.545472 Y45.613907 Z8 E16363.807302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.587031 Y45.333736 Z8 E16364.973744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.620812 Y45.106006 Z8 E16365.930896 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.620992 Y45.104795 Z8 E16365.935986 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.702383 Y44.556101 Z7.737636 E16368.487107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.705449 Y44.54386 Z7.731326 E16368.545764 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.746829 Y44.378661 Z7.652265 E16369.326379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.748254 Y44.372973 Z7.655196 E16369.353633 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X63.962221 Y43.518768 Z7.220833 E16373.435883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X64.322485 Y42.511899 Z6.686142 E16378.406628 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X64.779704 Y41.54519 Z6.151452 E16383.377372 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X65.329476 Y40.627951 Z5.616761 E16388.348117 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=5.616761 note=collision lift
G1 X65.966505 Y39.769016 Z5.082071 E16393.318862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X66.684657 Y38.976657 Z4.547381 E16398.289606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X67.477016 Y38.258505 Z4.01269 E16403.260351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X67.497402 Y38.243386 Z4 E16403.378324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.01269 matz1=4 note=collision lift
G1 X68.335951 Y37.621476 Z4 E16407.718775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X69.25319 Y37.071704 Z4 E16412.164744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X70.219899 Y36.614485 Z4 E16416.610713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X71.226768 Y36.254221 Z4 E16421.056682 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X72.264101 Y35.994383 Z4 E16425.502651 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X73.321907 Y35.837472 Z4 E16429.94862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X74.39 Y35.785 Z4 E16434.394589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X75.458093 Y35.837472 Z4 E16438.840558 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X76.515899 Y35.994383 Z4 E16443.286528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X77.553232 Y36.254221 Z4 E16447.732497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X78.560101 Y36.614485 Z4 E16452.178466 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X78.909425 Y36.779702 Z4 E16453.785032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X79.52681 Y37.071704 Z4.341478 E16456.959581 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4 matz1=4.341478 note=collision lift
G1 X80.444049 Y37.621476 Z4.876169 E16461.930326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X81.302984 Y38.258505 Z5.410859 E16466.90107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X82.095343 Y38.976657 Z5.94555 E16471.871815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X82.813495 Y39.769016 Z6.48024 E16476.842559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.94555 matz1=6 note=collision lift
G1 X83.450524 Y40.627951 Z7.014931 E16481.813304 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X84.000296 Y41.54519 Z7.549621 E16486.784049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X84.38542 Y42.359465 Z8 E16490.970993 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X84.457515 Y42.511899 Z8 E16491.672045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X84.817779 Y43.518768 Z8 E16496.118014 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X85.077617 Y44.556101 Z8 E16500.563983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X85.234528 Y45.613907 Z8 E16505.009953 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X85.287 Y46.682 Z8 E16509.455922 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X85.234528 Y47.750093 Z8 E16513.901891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X85.159188 Y48.257994 Z8 E16516.036603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X85.159008 Y48.259205 Z8 E16516.041692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X85.158819 Y48.260482 Z8 E16516.04706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X85.077617 Y48.807899 Z8 E16518.34786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X84.817779 Y49.845232 Z8 E16522.793829 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X84.457515 Y50.852101 Z8 E16527.239798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X84.38542 Y51.004535 Z8 E16527.94085 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X84.000296 Y51.81881 Z7.549621 E16532.127795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X83.450524 Y52.736049 Z7.014931 E16537.098539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X82.813495 Y53.594984 Z6.48024 E16542.069284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=6 note=collision lift
G1 X82.095343 Y54.387343 Z5.94555 E16547.040029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=5.94555 note=collision lift
G1 X81.302984 Y55.105495 Z5.410859 E16552.010773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.94555 matz1=5.410859 note=collision lift
G1 X80.444049 Y55.742524 Z4.876169 E16556.981518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.410859 matz1=4.876169 note=collision lift
G1 X79.52681 Y56.292296 Z4.341478 E16561.952262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.876169 matz1=4.341478 note=collision lift
G1 X78.909425 Y56.584298 Z4 E16565.126812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.341478 matz1=4 note=collision lift
G1 X78.560101 Y56.749515 Z4 E16566.733378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X77.553232 Y57.109779 Z4 E16571.179347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X76.515899 Y57.369617 Z4 E16575.625316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X75.458093 Y57.526528 Z4 E16580.071285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X74.977081 Y57.550159 Z4 E16582.07351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025
G1 X74.455074 Y57.575803 Z4.261318 E16584.502855 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4 matz1=4.261318 note=collision lift
G1 X74.39 Y57.579 Z4.293895 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.261318 matz1=4.293895 note=collision lift
G1 X73.321907 Y57.526528 Z4.828585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.293895 matz1=4.828585 note=collision lift
G1 X72.264101 Y57.369617 Z5.363276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=4.828585 matz1=5.363276 note=collision lift
G1 X71.226768 Y57.109779 Z5.897966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.363276 matz1=5.897966 note=collision lift
G1 X71.034205 Y57.040879 Z6.000225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.897966 matz1=6 note=collision lift
G1 X70.219899 Y56.749515 Z5.567794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=6 matz1=5.567794 note=collision lift
G1 X70.102868 Y56.694164 Z5.503064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0025 matz0=5.567794 matz1=5.503064 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0025
G0 X70.102868 Y56.694164 Z9.503064 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0024 note=intra-page lift
G0 X63.741617 Y70.143899 Z9.503064 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0024 note=intra-page XY
G0 X63.741617 Y70.143899 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0024 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0024
G1 X63.481779 Y71.181232 Z4 E16584.661336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X63.336708 Y71.586679 Z4 E16584.814668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X63.121515 Y72.188101 Z4 E16585.136779 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X62.753288 Y72.966651 Z4 E16585.75011 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X62.664296 Y73.15481 Z4 E16585.929185 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X62.114524 Y74.072049 Z4 E16587.038553 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X61.981995 Y74.250744 Z4 E16587.309178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X61.477495 Y74.930984 Z4 E16588.464883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X61.038903 Y75.414895 Z4 E16589.491875 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X60.759343 Y75.723343 Z4 E16590.208176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X59.966984 Y76.441495 Z4 E16592.268431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X59.955471 Y76.450034 Z4 E16592.298199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X59.108049 Y77.078524 Z4 E16594.645648 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X58.7264 Y77.307276 Z4 E16595.72815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X58.19081 Y77.628296 Z4 E16597.339827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X57.399303 Y78.002651 Z4 E16599.781729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X57.306038 Y78.046762 Z4 E16600.083455 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=prime ramp
G1 X57.224101 Y78.085515 Z4.04532 E16600.382695 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4 matz1=4.04532 note=collision lift
G1 X56.217232 Y78.445779 Z4.58001 E16604.128088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.04532 matz1=4.58001 note=collision lift
G1 X56.130567 Y78.467487 Z4.624682 E16604.458936 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.58001 matz1=4.624682 note=collision lift
G1 X55.179899 Y78.705617 Z5.114701 E16608.269684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.624682 matz1=5.114701 note=collision lift
G1 X55.179807 Y78.705631 Z5.114747 E16608.270064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X54.82221 Y78.758675 Z5.295502 E16609.75977 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.114747 matz1=5.295502 note=collision lift
G1 X54.122093 Y78.862528 Z5.649391 E16612.807483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.295502 matz1=5.649391 note=collision lift
G1 X53.488993 Y78.89363 Z5.96632 E16615.684231 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.649391 matz1=5.965892 note=collision lift
G1 X53.420766 Y78.896982 Z6.000475 E16616.001748 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.965892 matz1=6 note=collision lift
G1 X53.419817 Y78.897029 Z6 E16616.006162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y78.915 Z6 E16617.528888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y78.862528 Z6 E16621.974858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y78.705617 Z6 E16626.420827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y78.445779 Z6 E16630.866796 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y78.085515 Z6 E16635.312765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y77.628296 Z6 E16639.758734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X47.603039 Y77.440001 Z6 E16641.281461 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X47.602225 Y77.439513 Z6.000475 E16641.285874 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X46.999951 Y77.078524 Z5.649391 E16644.54974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=5.649391 note=collision lift
G1 X46.141092 Y76.441551 Z5.114747 E16649.52005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X46.141016 Y76.441495 Z5.114701 E16649.520485 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X45.348657 Y75.723343 Z4.58001 E16654.49123 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X44.630505 Y74.930984 Z4.04532 E16659.461974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X44.576511 Y74.858181 Z4 E16659.883288 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.04532 matz1=4 note=collision lift
G1 X43.993476 Y74.072049 Z4 E16663.952423 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X43.443704 Y73.15481 Z4 E16668.398392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.986485 Y72.188101 Z4 E16672.844361 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.626221 Y71.181232 Z4 E16677.29033 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.366383 Y70.143899 Z4 E16681.736299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.209472 Y69.086093 Z4 E16686.182268 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.157 Y68.018 Z4 E16690.628237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.209472 Y66.949907 Z4 E16695.074206 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.366383 Y65.892101 Z4 E16699.520176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.626221 Y64.854768 Z4 E16703.966145 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X42.986485 Y63.847899 Z4 E16708.412114 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X43.151702 Y63.498575 Z4 E16710.01868 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X43.443704 Y62.88119 Z4.341478 E16713.193229 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4 matz1=4.341478 note=collision lift
G1 X43.993476 Y61.963951 Z4.876169 E16718.163974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X44.630505 Y61.105016 Z5.410859 E16723.134718 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X45.348657 Y60.312657 Z5.94555 E16728.105463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X46.141016 Y59.594505 Z6.48024 E16733.076207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.94555 matz1=6 note=collision lift
G1 X46.999951 Y58.957476 Z7.014931 E16738.046952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y58.407704 Z7.549621 E16743.017697 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X48.731465 Y58.02258 Z8 E16747.204641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y57.950485 Z8 E16747.905693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y57.590221 Z8 E16752.351662 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y57.330383 Z8 E16756.797631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y57.173472 Z8 E16761.2436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y57.121 Z8 E16765.68957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X54.122093 Y57.173472 Z8 E16770.135539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X54.629994 Y57.248812 Z8 E16772.270251 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X54.631205 Y57.248992 Z8 E16772.27534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X55.179899 Y57.330383 Z7.737636 E16774.826462 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X55.19214 Y57.333449 Z7.731326 E16774.885118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X55.357339 Y57.374829 Z7.652265 E16775.665733 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X55.363027 Y57.376254 Z7.655196 E16775.692988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X56.217232 Y57.590221 Z7.220833 E16779.775238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X57.224101 Y57.950485 Z6.686142 E16784.745982 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X58.19081 Y58.407704 Z6.151452 E16789.716727 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=6 note=collision lift
G1 X59.108049 Y58.957476 Z5.616761 E16794.687471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=6 matz1=5.616761 note=collision lift
G1 X59.966984 Y59.594505 Z5.082071 E16799.658216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X60.759343 Y60.312657 Z4.547381 E16804.628961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X61.477495 Y61.105016 Z4.01269 E16809.599705 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X61.492614 Y61.125402 Z4 E16809.717678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 matz0=4.01269 matz1=4 note=collision lift
G1 X62.114524 Y61.963951 Z4 E16814.058129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X62.664296 Y62.88119 Z4 E16818.504098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X63.121515 Y63.847899 Z4 E16822.950067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X63.481779 Y64.854768 Z4 E16827.396036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X63.56607 Y65.191276 Z4 E16828.838298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024
G1 X63.741617 Y65.892101 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=end-early tail
G1 X63.898528 Y66.949907 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=end-early tail
G1 X63.951 Y68.018 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=end-early tail
G1 X63.898528 Y69.086093 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=end-early tail
G1 X63.741617 Y70.143899 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0024 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0024
G0 X63.741617 Y70.143899 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0023 note=intra-page lift
G0 X74.639048 Y72.390962 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0023 note=intra-page XY
G0 X74.639048 Y72.390962 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0023 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0023
G1 X73.209588 Y72.824584 Z4 E16829.147531 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X73.203399 Y72.825193 Z4 E16829.150111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X71.723 Y72.971 Z4 E16830.075232 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X71.710622 Y72.969781 Z4 E16830.085553 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X70.236412 Y72.824584 Z4 E16831.621401 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X70.218559 Y72.819168 Z4 E16831.644622 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X68.806952 Y72.390962 Z4 E16833.786036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X68.785014 Y72.379236 Z4 E16833.827318 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X67.489555 Y71.686798 Z4 E16836.569139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X67.465519 Y71.667073 Z4 E16836.633642 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X66.334846 Y70.739154 Z4 E16839.970709 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X66.311175 Y70.710311 Z4 E16840.063593 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X65.387202 Y69.584445 Z4 E16843.990747 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X65.366681 Y69.546054 Z4 E16844.117172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X64.683038 Y68.267048 Z4 E16848.629252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X64.668596 Y68.21944 Z4 E16848.794379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X64.249416 Y66.837588 Z4 E16853.886224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X64.24393 Y66.781889 Z4 E16854.095213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X64.103 Y65.351 Z4 E16859.761663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X64.109095 Y65.289112 Z4 E16860.019674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=prime ramp
G1 X64.249416 Y63.864412 Z4 E16865.971548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023
G1 X64.496051 Y63.051365 Z4 E16869.503905 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023
G1 X64.683038 Y62.434952 Z4.322075 E16872.498071 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=4 matz1=4.322075 note=collision lift
G1 X65.387202 Y61.117555 Z5.068966 E16879.441533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=4.322075 matz1=5.068966 note=collision lift
G1 X66.334846 Y59.962846 Z5.815856 E16886.384994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=5.068966 matz1=5.815856 note=collision lift
G1 X67.489555 Y59.015202 Z6.562747 E16893.328455 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=5.815856 matz1=6 note=collision lift
G1 X68.806952 Y58.311038 Z7.309637 E16900.271917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X70.13426 Y57.908404 Z8 E16906.713332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X70.140296 Y57.906573 Z8 E16906.739556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X70.236412 Y57.877416 Z8 E16907.15714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X71.723 Y57.731 Z8 E16913.367561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X72.053758 Y57.763577 Z8 E16914.749348 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X72.054087 Y57.763609 Z8 E16914.750722 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X72.277319 Y57.785596 Z7.89856 E16915.774229 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X72.278265 Y57.785689 Z7.899035 E16915.778648 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X73.209588 Y57.877416 Z7.455069 E16920.085007 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X74.639048 Y58.311038 Z6.708179 E16927.028469 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=6 note=collision lift
G1 X75.956445 Y59.015202 Z5.961288 E16933.97193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=6 matz1=5.961288 note=collision lift
G1 X77.111154 Y59.962846 Z5.214398 E16940.915391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=5.961288 matz1=5.214398 note=collision lift
G1 X78.058798 Y61.117555 Z4.467507 E16947.858853 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=5.214398 matz1=4.467507 note=collision lift
G1 X78.499561 Y61.942163 Z4 E16952.205027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 matz0=4.467507 matz1=4 note=collision lift
G1 X78.762962 Y62.434952 Z4 E16954.528111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023
G1 X79.196584 Y63.864412 Z4 E16960.738532 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023
G1 X79.343 Y65.351 Z4 E16966.948952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023
G1 X79.196584 Y66.837588 Z4 E16973.159373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023
G1 X78.762962 Y68.267048 Z4 E16979.369794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023
G1 X78.303291 Y69.127031 Z4 E16983.423892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023
G1 X78.058798 Y69.584445 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=end-early tail
G1 X77.111154 Y70.739154 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=end-early tail
G1 X75.956445 Y71.686798 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=end-early tail
G1 X74.639048 Y72.390962 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0023 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0023
G0 X74.639048 Y72.390962 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0022 note=intra-page lift
G0 X79.841034 Y85.481134 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0022 note=intra-page XY
G0 X79.841034 Y85.481134 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0022 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0022
G1 X78.795628 Y84.405435 Z4 E16983.735706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X78.550475 Y84.153178 Z4 E16983.899097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X77.803342 Y83.281254 Z4 E16984.671147 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X77.46233 Y82.883285 Z4 E16985.144992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X76.882819 Y82.098065 Z4 E16986.230216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X76.566609 Y81.669609 Z4 E16986.933684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X76.059615 Y80.845594 Z4 E16988.412912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X75.85332 Y80.510302 Z4 E16989.089069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X75.367588 Y79.516308 Z4 E16991.219236 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X75.312471 Y79.403518 Z4 E16991.482381 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X74.93407 Y78.347407 Z4 E16994.027895 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X74.87878 Y78.100923 Z4 E16994.649187 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X74.708125 Y77.340125 Z4 E16996.678416 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X74.645744 Y76.622535 Z4 E16998.702766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X74.624645 Y76.379823 Z4 E16999.42001 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X74.673639 Y75.464654 Z4 E17002.265492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X74.73923 Y75.131149 Z4 E17003.379973 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X74.845114 Y74.592772 Z4 E17005.246649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X75.129078 Y73.762328 Z4 E17008.40595 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X75.161417 Y73.69615 Z4 E17008.680807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X75.515541 Y72.971476 Z4 E17011.788958 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X75.887671 Y72.386357 Z4 E17014.605268 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=prime ramp
G1 X75.99451 Y72.218369 Z4 E17015.432964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X77.19 Y70.818 Z4 E17023.088025 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X78.590369 Y69.62251 Z4 E17030.743086 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X79.343476 Y69.143541 Z4 E17034.453729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X80.134328 Y68.757078 Z4 E17038.113288 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X80.964772 Y68.473114 Z4 E17041.76214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X81.836654 Y68.301639 Z4 E17045.456446 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X82.751823 Y68.252645 Z4 E17049.266724 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X83.712125 Y68.336125 Z4 E17053.274253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X84.719407 Y68.56207 Z4 E17057.566109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X85.775518 Y68.940471 Z4 E17062.230235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X86.882302 Y69.48132 Z4 E17067.351734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X88.041609 Y70.194609 Z4 E17073.010806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X89.255285 Y71.09033 Z4 E17079.28208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X90.525178 Y72.178475 Z4 E17086.234817 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X91.853134 Y73.469034 Z4 E17093.933534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X93.241 Y74.972 Z4 E17102.438762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X94.771059 Y76.185973 Z4 E17110.559031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X96.838094 Y78.173219 Z4 E17122.480149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X99.26977 Y80.900855 Z4 E17137.672474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X101.89375 Y84.336 Z4 E17155.644055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X103.224 Y86.308612 Z4 E17165.535766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X104.537699 Y88.44577 Z4 E17175.965459 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X105.813307 Y90.743363 Z4 E17186.891197 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X107.029281 Y93.197281 Z4 E17198.27726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X108.16408 Y95.803415 Z4 E17210.094923 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X109.19616 Y98.557652 Z4 E17222.323265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X110.103981 Y101.455884 Z4 E17234.949998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X110.866 Y104.494 Z4 E17247.972268 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X107.827884 Y103.731981 Z4 E17260.994537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X104.929652 Y102.82416 Z4 E17273.62127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X102.175415 Y101.79208 Z4 E17285.849612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X99.569281 Y100.657281 Z4 E17297.667275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X97.115363 Y99.441307 Z4 E17309.053338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X94.81777 Y98.165699 Z4 E17319.979076 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X92.680612 Y96.852 Z4 E17330.408769 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X90.708 Y95.52175 Z4 E17340.30048 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X87.272855 Y92.89777 Z4 E17358.272061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X84.545219 Y90.466094 Z4 E17373.464386 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X83.251791 Y89.120734 Z4 E17381.223416 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022
G1 X82.557973 Y88.399059 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=end-early tail
G1 X81.344 Y86.869 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=end-early tail
G1 X79.841034 Y85.481134 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0022 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0022
G0 X79.841034 Y85.481134 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0021 note=intra-page lift
G0 X70.164416 Y95.846588 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0021 note=intra-page XY
G0 X70.164416 Y95.846588 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0021 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0021
G1 X70.018 Y94.36 Z4 E17381.53265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X70.01861 Y94.353811 Z4 E17381.53523 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X70.164416 Y92.873412 Z4 E17382.460351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X70.168027 Y92.86151 Z4 E17382.470671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X70.598038 Y91.443952 Z4 E17384.006519 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X70.606833 Y91.427499 Z4 E17384.02974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X71.302202 Y90.126555 Z4 E17386.171155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X71.317982 Y90.107326 Z4 E17386.212436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X72.249846 Y88.971846 Z4 E17388.954258 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X72.273882 Y88.952121 Z4 E17389.01876 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X73.404555 Y88.024202 Z4 E17392.355828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X73.437462 Y88.006612 Z4 E17392.448712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X74.721952 Y87.320038 Z4 E17396.375865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X74.763609 Y87.307401 Z4 E17396.502291 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X76.151412 Y86.886416 Z4 E17401.01437 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X76.200922 Y86.88154 Z4 E17401.179497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X77.638 Y86.74 Z4 E17406.271342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X77.6937 Y86.745486 Z4 E17406.480331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X79.124588 Y86.886416 Z4 E17412.146782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X79.184098 Y86.904468 Z4 E17412.404793 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=prime ramp
G1 X80.554048 Y87.320038 Z4 E17418.356666 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X81.871445 Y88.024202 Z4 E17424.567087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X83.026154 Y88.971846 Z4 E17430.777508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X83.973798 Y90.126555 Z4 E17436.987928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X84.677962 Y91.443952 Z4 E17443.198349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X85.111584 Y92.873412 Z4 E17449.40877 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X85.258 Y94.36 Z4 E17455.61919 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X85.111584 Y95.846588 Z4 E17461.829611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X84.677962 Y97.276048 Z4 E17468.040032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X83.973798 Y98.593445 Z4 E17474.250452 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X83.026154 Y99.748154 Z4 E17480.460873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X81.871445 Y100.695798 Z4 E17486.671293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X80.554048 Y101.399962 Z4 E17492.881714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X79.124588 Y101.833584 Z4 E17499.092135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X77.638 Y101.98 Z4 E17505.302555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X76.151412 Y101.833584 Z4 E17511.512976 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X74.721952 Y101.399962 Z4 E17517.723397 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X73.404555 Y100.695798 Z4 E17523.933817 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X72.650773 Y100.077186 Z4 E17527.987915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021
G1 X72.249846 Y99.748154 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=end-early tail
G1 X71.302202 Y98.593445 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=end-early tail
G1 X70.598038 Y97.276048 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=end-early tail
G1 X70.164416 Y95.846588 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0021 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0021
G0 X70.164416 Y95.846588 Z8.04532 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0020 note=intra-page lift
G0 X57.224101 Y99.421515 Z8.04532 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0020 note=intra-page XY
G0 X57.224101 Y99.421515 Z4.04532 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0020 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0020
G1 X56.562975 Y99.65807 Z4.396403 E17528.073325 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.04532 matz1=4.396403 note=collision lift
G1 X56.562805 Y99.658131 Z4.396313 E17528.073369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.396403 matz1=4.396313 note=collision lift
G1 X56.221337 Y99.78031 Z4.577646 E17528.184404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.396313 matz1=4.577646 note=collision lift
G1 X56.217232 Y99.781779 Z4.58001 E17528.186044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.577646 matz1=4.58001 note=collision lift
G1 X55.953203 Y99.847915 Z4.716102 E17528.299729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.58001 matz1=4.716102 note=collision lift
G1 X55.536103 Y99.952393 Z4.931094 E17528.531625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.716102 matz1=4.931094 note=collision lift
G1 X55.535928 Y99.952437 Z4.931004 E17528.531736 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.931094 matz1=4.931004 note=collision lift
G1 X55.188356 Y100.039499 Z5.110157 E17528.773928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.931004 matz1=5.110157 note=collision lift
G1 X55.179899 Y100.041617 Z5.114701 E17528.780431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.110157 matz1=5.114701 note=collision lift
G1 X54.641419 Y100.121493 Z5.386885 E17529.23517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.114701 matz1=5.386885 note=collision lift
G1 X54.485327 Y100.144647 Z5.465784 E17529.386182 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.386885 matz1=5.465784 note=collision lift
G1 X54.485148 Y100.144674 Z5.465694 E17529.38636 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.465784 matz1=5.465694 note=collision lift
G1 X54.135027 Y100.196609 Z5.642669 E17529.756487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.465694 matz1=5.642669 note=collision lift
G1 X54.122093 Y100.198528 Z5.649391 E17529.771074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.642669 matz1=5.649391 note=collision lift
G1 X53.420766 Y100.232982 Z6.000475 E17530.636996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.649391 matz1=6 note=collision lift
G1 X53.419817 Y100.233029 Z6 E17530.638283 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X53.293143 Y100.239252 Z6 E17530.794239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y100.251 Z6 E17531.100816 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y100.198528 Z6 E17532.664055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X51.796789 Y100.170475 Z6 E17532.976936 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y100.041617 Z6 E17534.544256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X50.324929 Y99.890531 Z6 E17535.783259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y99.781779 Z6 E17536.74142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X48.899863 Y99.427227 Z6 E17539.213211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y99.421515 Z6 E17539.255546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y98.964296 Z6 E17542.086634 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X47.603039 Y98.776001 Z6 E17543.12914 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X47.602225 Y98.775513 Z6.000475 E17543.132215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X47.566671 Y98.754203 Z5.979749 E17543.26679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=5.979303 note=collision lift
G1 X46.999951 Y98.414524 Z5.649391 E17545.492248 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.979303 matz1=5.649391 note=collision lift
G1 X46.453031 Y98.008901 Z5.308931 E17547.943996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.649391 matz1=5.308931 note=collision lift
G1 X46.141092 Y97.777551 Z5.114747 E17549.414305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.308931 matz1=5.114747 note=collision lift
G1 X46.141016 Y97.777495 Z5.114701 E17549.414666 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X45.434757 Y97.137378 Z4.638111 E17553.24483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.114701 matz1=4.638111 note=collision lift
G1 X45.348657 Y97.059343 Z4.58001 E17553.733287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.638111 matz1=4.58001 note=collision lift
G1 X44.630505 Y96.266984 Z4.04532 E17558.44811 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X44.576511 Y96.194181 Z4 E17558.865947 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.04532 matz1=4 note=collision lift
G1 X44.532941 Y96.135434 Z4 E17559.169292 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X43.993476 Y95.408049 Z4 E17562.93434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X43.443704 Y94.49081 Z4 E17567.380309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.986485 Y93.524101 Z4 E17571.826278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.626221 Y92.517232 Z4 E17576.272247 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.366383 Y91.479899 Z4 E17580.718216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.209472 Y90.422093 Z4 E17585.164185 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.157 Y89.354 Z4 E17589.610154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.209472 Y88.285907 Z4 E17594.056124 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.366383 Y87.228101 Z4 E17598.502093 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.626221 Y86.190768 Z4 E17602.948062 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X42.986485 Y85.183899 Z4 E17607.394031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X43.151702 Y84.834575 Z4 E17609.000597 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X43.443704 Y84.21719 Z4.341478 E17612.175146 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4 matz1=4.341478 note=collision lift
G1 X43.993476 Y83.299951 Z4.876169 E17617.145891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X44.630505 Y82.441016 Z5.410859 E17622.116635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X45.348657 Y81.648657 Z5.94555 E17627.08738 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X46.141016 Y80.930505 Z6.48024 E17632.058125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.94555 matz1=6 note=collision lift
G1 X46.999951 Y80.293476 Z7.014931 E17637.028869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y79.743704 Z7.549621 E17641.999614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X48.731465 Y79.35858 Z8 E17646.186558 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y79.286485 Z8 E17646.88761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y78.926221 Z8 E17651.333579 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y78.666383 Z8 E17655.779549 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y78.509472 Z8 E17660.225518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y78.457 Z8 E17664.671487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X54.122093 Y78.509472 Z8 E17669.117456 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X54.629994 Y78.584812 Z8 E17671.252168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X54.631205 Y78.584992 Z8 E17671.257257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X55.179899 Y78.666383 Z7.737636 E17673.808379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X55.19214 Y78.669449 Z7.731326 E17673.867036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X55.357339 Y78.710829 Z7.652265 E17674.64765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X55.363027 Y78.712254 Z7.655196 E17674.674905 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X56.217232 Y78.926221 Z7.220833 E17678.757155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X57.224101 Y79.286485 Z6.686142 E17683.7279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X58.19081 Y79.743704 Z6.151452 E17688.698644 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=6 note=collision lift
G1 X59.108049 Y80.293476 Z5.616761 E17693.669389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=5.616761 note=collision lift
G1 X59.966984 Y80.930505 Z5.082071 E17698.640133 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X60.759343 Y81.648657 Z4.547381 E17703.610878 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X61.477495 Y82.441016 Z4.01269 E17708.581622 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X61.492614 Y82.461402 Z4 E17708.699596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.01269 matz1=4 note=collision lift
G1 X62.114524 Y83.299951 Z4 E17713.040046 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X62.664296 Y84.21719 Z4 E17717.486015 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.121515 Y85.183899 Z4 E17721.931985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.481779 Y86.190768 Z4 E17726.377954 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.741617 Y87.228101 Z4 E17730.823923 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.898528 Y88.285907 Z4 E17735.269892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.951 Y89.354 Z4 E17739.715861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.898528 Y90.422093 Z4 E17744.16183 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.741617 Y91.479899 Z4 E17748.607799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.481779 Y92.517232 Z4 E17753.053768 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X63.121515 Y93.524101 Z4 E17757.499738 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X62.664296 Y94.49081 Z4 E17761.945707 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X62.114524 Y95.408049 Z4 E17766.391676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X61.477495 Y96.266984 Z4 E17770.837645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X61.473875 Y96.270978 Z4 E17770.860058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X60.896428 Y96.908092 Z4.42993 E17774.856898 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4 matz1=4.42993 note=collision lift
G1 X60.759343 Y97.059343 Z4.531995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.42993 matz1=4.531995 note=collision lift
G1 X59.966984 Y97.777495 Z5.066685 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=4.531995 matz1=5.066685 note=collision lift
G1 X59.108049 Y98.414524 Z5.601376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.066685 matz1=5.601376 note=collision lift
G1 X58.346373 Y98.871055 Z6.045383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.601376 matz1=6 note=collision lift
G1 X58.19081 Y98.964296 Z5.9547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=6 matz1=5.9547 note=collision lift
G1 X57.3056 Y99.382969 Z5.465087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.9547 matz1=5.465087 note=collision lift
G1 X57.305568 Y99.382985 Z5.465087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.465087 matz1=5.465087 note=collision lift
G1 X57.224101 Y99.421515 Z5.46487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 matz0=5.465087 matz1=5.46487 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0020
G0 X57.224101 Y99.421515 Z9.46487 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0019 note=intra-page lift
G0 X63.121515 Y114.860101 Z9.46487 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0019 note=intra-page XY
G0 X63.121515 Y114.860101 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0019 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0019
G1 X62.664296 Y115.82681 Z4 E17775.015379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X62.442914 Y116.196165 Z4 E17775.168712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X62.114524 Y116.744049 Z4 E17775.490823 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X61.601485 Y117.435802 Z4 E17776.104153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X61.477495 Y117.602984 Z4 E17776.283228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X60.759343 Y118.395343 Z4 E17777.392596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X60.594498 Y118.544749 Z4 E17777.663222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X59.966984 Y119.113495 Z4 E17778.818927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X59.442412 Y119.502543 Z4 E17779.845918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X59.108049 Y119.750524 Z4 E17780.562219 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X58.19081 Y120.300296 Z4 E17782.622474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X58.177853 Y120.306424 Z4 E17782.652242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X57.306038 Y120.718762 Z4 E17784.785907 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X57.224101 Y120.757515 Z4.04532 E17785.025075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4 matz1=4.04532 note=collision lift
G1 X56.858397 Y120.888366 Z4.239524 E17786.082193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.04532 matz1=4.239524 note=collision lift
G1 X56.217232 Y121.117779 Z4.58001 E17788.061719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.239524 matz1=4.58001 note=collision lift
G1 X55.576363 Y121.278308 Z4.910345 E17790.135772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.58001 matz1=4.910345 note=collision lift
G1 X55.179899 Y121.377617 Z5.114701 E17791.494566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.910345 matz1=5.114701 note=collision lift
G1 X55.179807 Y121.377631 Z5.114747 E17791.494884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X54.257068 Y121.514506 Z5.581165 E17794.812979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.114747 matz1=5.581165 note=collision lift
G1 X54.122093 Y121.534528 Z5.649391 E17795.323615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.581165 matz1=5.649391 note=collision lift
G1 X53.420766 Y121.568982 Z6.000475 E17798.053313 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.649391 matz1=6 note=collision lift
G1 X53.419817 Y121.569029 Z6 E17798.05712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y121.587 Z6 E17799.389181 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X52.859165 Y121.577428 Z6 E17800.113813 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y121.534528 Z6 E17803.491216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X51.366991 Y121.44272 Z6 E17806.038275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y121.377617 Z6 E17807.882932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y121.117779 Z6 E17812.328901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y120.757515 Z6 E17816.77487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y120.300296 Z6 E17821.220839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X47.603039 Y120.112001 Z6 E17822.743566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X47.602225 Y120.111513 Z6.000475 E17822.74798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X46.999951 Y119.750524 Z5.649391 E17826.011846 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=5.649391 note=collision lift
G1 X46.141092 Y119.113551 Z5.114747 E17830.982155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X46.141016 Y119.113495 Z5.114701 E17830.98259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X45.348657 Y118.395343 Z4.58001 E17835.953335 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X44.630505 Y117.602984 Z4.04532 E17840.924079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X44.576511 Y117.530181 Z4 E17841.345393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.04532 matz1=4 note=collision lift
G1 X43.993476 Y116.744049 Z4 E17845.414528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X43.443704 Y115.82681 Z4 E17849.860497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.986485 Y114.860101 Z4 E17854.306466 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.626221 Y113.853232 Z4 E17858.752435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.366383 Y112.815899 Z4 E17863.198404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.209472 Y111.758093 Z4 E17867.644373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.157 Y110.69 Z4 E17872.090342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.209472 Y109.621907 Z4 E17876.536312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.366383 Y108.564101 Z4 E17880.982281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.626221 Y107.526768 Z4 E17885.42825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X42.986485 Y106.519899 Z4 E17889.874219 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X43.151702 Y106.170575 Z4 E17891.480785 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X43.443704 Y105.55319 Z4.341478 E17894.655334 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4 matz1=4.341478 note=collision lift
G1 X43.993476 Y104.635951 Z4.876169 E17899.626079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X44.630505 Y103.777016 Z5.410859 E17904.596823 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X45.348657 Y102.984657 Z5.94555 E17909.567568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X46.141016 Y102.266505 Z6.48024 E17914.538312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.94555 matz1=6 note=collision lift
G1 X46.999951 Y101.629476 Z7.014931 E17919.509057 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y101.079704 Z7.549621 E17924.479802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X48.731465 Y100.69458 Z8 E17928.666746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y100.622485 Z8 E17929.367798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y100.262221 Z8 E17933.813767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y100.002383 Z8 E17938.259737 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y99.845472 Z8 E17942.705706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y99.793 Z8 E17947.151675 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X54.122093 Y99.845472 Z8 E17951.597644 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X54.629994 Y99.920812 Z8 E17953.732356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X54.631205 Y99.920992 Z8 E17953.737445 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X55.179899 Y100.002383 Z7.737636 E17956.288567 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X55.19214 Y100.005449 Z7.731326 E17956.347224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X55.363027 Y100.048254 Z7.649543 E17957.154714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X55.370566 Y100.050142 Z7.645657 E17957.190838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X55.375598 Y100.051403 Z7.643163 E17957.214768 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X55.376593 Y100.051652 Z7.643676 E17957.219538 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X55.734255 Y100.141242 Z7.467151 E17958.919092 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X55.735323 Y100.141509 Z7.467701 E17958.924206 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X56.043035 Y100.218587 Z7.309092 E17960.398716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X56.217232 Y100.262221 Z7.398881 E17961.233445 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X56.341509 Y100.306688 Z7.464878 E17961.84698 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X56.545744 Y100.379765 Z7.465085 E17962.748808 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X56.556421 Y100.383585 Z7.470754 E17962.801516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X56.90318 Y100.507657 Z7.510268 E17964.341467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X56.912383 Y100.51095 Z7.505381 E17964.386901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X57.061667 Y100.564365 Z7.502615 E17965.046184 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X57.063641 Y100.565071 Z7.503663 E17965.055929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X57.224101 Y100.622485 Z7.477489 E17965.772773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X57.246519 Y100.633087 Z7.46509 E17965.888043 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X57.319981 Y100.667833 Z7.464886 E17966.225904 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X58.19081 Y101.079704 Z6.983227 E17970.70364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X59.108049 Y101.629476 Z6.448537 E17975.674385 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=6 note=collision lift
G1 X59.966984 Y102.266505 Z5.913847 E17980.645129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=6 matz1=5.913847 note=collision lift
G1 X60.759343 Y102.984657 Z5.379156 E17985.615874 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.913847 matz1=5.379156 note=collision lift
G1 X61.477495 Y103.777016 Z4.844466 E17990.586618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=5.379156 matz1=4.844466 note=collision lift
G1 X62.114524 Y104.635951 Z4.309775 E17995.557363 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.844466 matz1=4.309775 note=collision lift
G1 X62.433037 Y105.167357 Z4 E17998.437185 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 matz0=4.309775 matz1=4 note=collision lift
G1 X62.664296 Y105.55319 Z4 E18000.307363 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X63.121515 Y106.519899 Z4 E18004.753332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X63.481779 Y107.526768 Z4 E18009.199301 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X63.741617 Y108.564101 Z4 E18013.64527 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X63.898528 Y109.621907 Z4 E18018.091239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X63.91555 Y109.968394 Z4 E18019.533501 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X63.951 Y110.69 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X63.898528 Y111.758093 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X63.741617 Y112.815899 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X63.481779 Y113.853232 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X63.121515 Y114.860101 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0019
G0 X63.121515 Y114.860101 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0018 note=intra-page lift
G0 X72.316732 Y119.038196 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0018 note=intra-page XY
G0 X72.316732 Y119.038196 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0018 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0018
G1 X72.19961 Y119.028469 Z4 E18019.535415 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X70.83502 Y118.806819 Z4 E18019.845314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X70.815453 Y118.803641 Z4 E18019.85361 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X69.586669 Y118.488256 Z4 E18020.611042 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X69.388259 Y118.414818 Z4 E18020.780756 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X68.50549 Y118.088076 Z4 E18021.686239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X68.007592 Y117.834609 Z4 E18022.339825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X67.564148 Y117.608862 Z4 E18022.994771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X66.754875 Y117.056375 Z4 E18024.485138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X66.738178 Y117.041262 Z4 E18024.522521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X66.069903 Y116.436376 Z4 E18026.134111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X65.686547 Y115.976605 Z4 E18027.328845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X65.501463 Y115.754627 Z4 E18027.941216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X65.041788 Y115.016888 Z4 E18029.922472 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.900201 Y114.705843 Z4 E18030.758796 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.683109 Y114.228922 Z4 E18032.103987 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.417659 Y113.396489 Z4 E18034.516218 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.396968 Y113.296343 Z4 E18034.812375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.23767 Y112.52535 Z4 E18037.189454 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.185514 Y111.814538 Z4 E18039.489582 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.103 Y110.69 Z4 E18043.416061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.130255 Y110.31856 Z4 E18044.790416 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.23767 Y108.85465 Z4 E18050.581336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.244176 Y108.823161 Z4 E18050.714877 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X64.417659 Y107.983511 Z4 E18054.279465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X64.683109 Y107.151078 Z4 E18057.912024 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X65.041788 Y106.363112 Z4 E18061.511438 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X65.501463 Y105.625373 Z4 E18065.125273 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X66.069903 Y104.943624 Z4 E18068.815654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X66.754875 Y104.323625 Z4 E18072.656771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X67.564148 Y103.771138 Z4 E18076.730639 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X68.50549 Y103.291924 Z4 E18081.122227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X69.586669 Y102.891744 Z4 E18085.915272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X70.815453 Y102.576359 Z4 E18091.18955 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X72.19961 Y102.351531 Z4 E18097.019625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X73.746908 Y102.223021 Z4 E18103.474692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X75.465115 Y102.196591 Z4 E18110.619013 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X77.362 Y102.278 Z4 E18118.512602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X79.16243 Y102.054242 Z4 E18126.055505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X81.822688 Y101.997688 Z4 E18137.11807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X85.208102 Y102.206914 Z4 E18151.219841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X89.184 Y102.7805 Z4 E18167.920835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X91.351296 Y103.234733 Z4 E18177.127176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X93.615711 Y103.817023 Z4 E18186.8478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X95.960411 Y104.539692 Z4 E18197.048443 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X98.368563 Y105.415063 Z4 E18207.701318 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X100.823331 Y106.455456 Z4 E18218.785843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X103.307883 Y107.673195 Z4 E18230.28939 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X105.805384 Y109.080603 Z4 E18242.207988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X108.299 Y110.69 Z4 E18254.546979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X105.805384 Y112.299397 Z4 E18266.885969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X103.307883 Y113.706805 Z4 E18278.804567 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X100.823331 Y114.924544 Z4 E18290.308114 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X98.368563 Y115.964938 Z4 E18301.39264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X95.960411 Y116.840308 Z4 E18312.045514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X93.615711 Y117.562977 Z4 E18322.246157 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X91.351296 Y118.145267 Z4 E18331.966781 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X89.184 Y118.5995 Z4 E18341.173123 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X85.208102 Y119.173086 Z4 E18357.874117 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X81.822688 Y119.382313 Z4 E18371.975887 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X79.16243 Y119.325758 Z4 E18383.038453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X77.362 Y119.102 Z4 E18390.581356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X77.309907 Y119.104236 Z4 E18390.798133 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X75.465115 Y119.183409 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=end-early tail
G1 X73.746908 Y119.156979 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=end-early tail
G1 X72.316732 Y119.038196 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0018
G0 X72.316732 Y119.038196 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0017 note=intra-page lift
G0 X71.302202 Y131.253445 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0017 note=intra-page XY
G0 X71.302202 Y131.253445 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0017 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0017
G1 X70.598038 Y129.936048 Z4 E18391.107367 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.596233 Y129.930097 Z4 E18391.109947 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.164416 Y128.506588 Z4 E18392.035068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.163197 Y128.494211 Z4 E18392.045389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.018 Y127.02 Z4 E18393.581236 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.019829 Y127.001433 Z4 E18393.604457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.164416 Y125.533412 Z4 E18395.745872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.171637 Y125.509608 Z4 E18395.787154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.598038 Y124.103952 Z4 E18398.528975 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X70.612696 Y124.07653 Z4 E18398.593478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X71.302202 Y122.786555 Z4 E18401.930545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X71.325872 Y122.757712 Z4 E18402.023429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X72.249846 Y121.631846 Z4 E18405.950583 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X72.283497 Y121.60423 Z4 E18406.077008 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X73.404555 Y120.684202 Z4 E18410.589087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X73.448431 Y120.660749 Z4 E18410.754214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X74.721952 Y119.980038 Z4 E18415.84606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X74.775511 Y119.963791 Z4 E18416.055048 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X76.151412 Y119.546416 Z4 E18421.721499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X76.2133 Y119.540321 Z4 E18421.97951 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X77.638 Y119.4 Z4 E18427.931384 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X79.124588 Y119.546416 Z4 E18434.141804 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X80.554048 Y119.980038 Z4 E18440.352225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X81.871445 Y120.684202 Z4 E18446.562646 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X83.026154 Y121.631846 Z4 E18452.773066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X83.973798 Y122.786555 Z4 E18458.983487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X84.677962 Y124.103952 Z4 E18465.193908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X85.111584 Y125.533412 Z4 E18471.404328 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X85.258 Y127.02 Z4 E18477.614749 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X85.111584 Y128.506588 Z4 E18483.825169 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X84.677962 Y129.936048 Z4 E18490.03559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X83.973798 Y131.253445 Z4 E18496.246011 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X83.026154 Y132.408154 Z4 E18502.456431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X81.871445 Y133.355798 Z4 E18508.666852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X80.554048 Y134.059962 Z4 E18514.877273 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X79.124588 Y134.493584 Z4 E18521.087693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X77.638 Y134.64 Z4 E18527.298114 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X76.151412 Y134.493584 Z4 E18533.508535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X75.218275 Y134.21052 Z4 E18537.562633 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X74.721952 Y134.059962 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=end-early tail
G1 X73.404555 Y133.355798 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=end-early tail
G1 X72.249846 Y132.408154 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=end-early tail
G1 X71.302202 Y131.253445 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0017
G0 X71.302202 Y131.253445 Z9.267162 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0016 note=intra-page lift
G0 X54.878559 Y142.758317 Z9.267162 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0016 note=intra-page XY
G0 X54.878559 Y142.758317 Z5.267162 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0016 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0016
G1 X54.485371 Y142.816641 Z5.465439 E18537.589977 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.267162 matz1=5.465439 note=collision lift
G1 X54.485327 Y142.816647 Z5.465604 E18537.589998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.465439 matz1=5.465604 note=collision lift
G1 X54.122203 Y142.870512 Z5.64915 E18537.663892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.465604 matz1=5.64915 note=collision lift
G1 X54.122093 Y142.870528 Z5.649391 E18537.663955 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.64915 matz1=5.649391 note=collision lift
G1 X53.545935 Y142.898833 Z5.937815 E18537.874446 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.649391 matz1=5.937425 note=collision lift
G1 X53.420766 Y142.904982 Z6.000475 E18537.935419 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.937425 matz1=6 note=collision lift
G1 X53.419817 Y142.905029 Z6 E18537.935901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y142.923 Z6 E18538.121096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X52.062628 Y142.874297 Z6 E18538.809888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y142.870528 Z6 E18538.874576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y142.713617 Z6 E18539.945018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X50.584898 Y142.627649 Z6 E18540.368957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y142.453779 Z6 E18541.332422 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X49.152197 Y142.189514 Z6 E18542.551653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y142.093515 Z6 E18543.036789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y141.636296 Z6 E18545.058118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X47.79225 Y141.56141 Z6 E18545.357977 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X47.603039 Y141.448001 Z6 E18545.823284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X47.602225 Y141.447513 Z6.000475 E18545.825556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X46.999951 Y141.086524 Z5.649391 E18547.59113 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=5.649391 note=collision lift
G1 X46.645565 Y140.823694 Z5.428784 E18548.787928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.649391 matz1=5.428784 note=collision lift
G1 X46.141092 Y140.449551 Z5.114747 E18550.607928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.428784 matz1=5.114747 note=collision lift
G1 X46.141016 Y140.449495 Z5.114701 E18550.60821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X45.612368 Y139.970356 Z4.757964 E18552.841507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.114701 matz1=4.757964 note=collision lift
G1 X45.348657 Y139.731343 Z4.58001 E18554.021492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.757964 matz1=4.58001 note=collision lift
G1 X44.686679 Y139.000963 Z4.087144 E18557.518714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.58001 matz1=4.087144 note=collision lift
G1 X44.630505 Y138.938984 Z4.04532 E18557.830978 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.087144 matz1=4.04532 note=collision lift
G1 X44.576511 Y138.866181 Z4 E18558.172079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.04532 matz1=4 note=collision lift
G1 X43.993476 Y138.080049 Z4 E18561.613001 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X43.825673 Y137.800087 Z4 E18562.819548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X43.443704 Y137.16281 Z4 E18565.676111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X43.120037 Y136.478473 Z4 E18568.744009 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X42.986485 Y136.196101 Z4 E18570.042661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X42.626221 Y135.189232 Z4 E18574.48863 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X42.366383 Y134.151899 Z4 E18578.934599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X42.209472 Y133.094093 Z4 E18583.380568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X42.157 Y132.026 Z4 E18587.826537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X42.209472 Y130.957907 Z4 E18592.272506 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X42.366383 Y129.900101 Z4 E18596.718475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X42.626221 Y128.862768 Z4 E18601.164444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X42.986485 Y127.855899 Z4 E18605.610414 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X43.151702 Y127.506575 Z4 E18607.216979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X43.443704 Y126.88919 Z4.341478 E18610.391529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4 matz1=4.341478 note=collision lift
G1 X43.993476 Y125.971951 Z4.876169 E18615.362273 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X44.630505 Y125.113016 Z5.410859 E18620.333018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X45.348657 Y124.320657 Z5.94555 E18625.303762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X46.141016 Y123.602505 Z6.48024 E18630.274507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.94555 matz1=6 note=collision lift
G1 X46.999951 Y122.965476 Z7.014931 E18635.245252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y122.415704 Z7.549621 E18640.215996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X48.731465 Y122.03058 Z8 E18644.402941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y121.958485 Z8 E18645.103993 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y121.598221 Z8 E18649.549962 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y121.338383 Z8 E18653.995931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y121.181472 Z8 E18658.4419 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y121.129 Z8 E18662.887869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X54.122093 Y121.181472 Z8 E18667.333838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X54.629994 Y121.256812 Z8 E18669.46855 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X54.631205 Y121.256992 Z8 E18669.47364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X55.179899 Y121.338383 Z7.737636 E18672.024761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X55.19214 Y121.341449 Z7.731326 E18672.083418 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X55.357339 Y121.382829 Z7.652265 E18672.864033 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X55.363027 Y121.384254 Z7.655196 E18672.891287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X56.217232 Y121.598221 Z7.220833 E18676.973537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X57.224101 Y121.958485 Z6.686142 E18681.944282 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X58.19081 Y122.415704 Z6.151452 E18686.915027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X59.108049 Y122.965476 Z5.616761 E18691.885771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=5.616761 note=collision lift
G1 X59.966984 Y123.602505 Z5.082071 E18696.856516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X60.759343 Y124.320657 Z4.547381 E18701.82726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X61.477495 Y125.113016 Z4.01269 E18706.798005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X61.492614 Y125.133402 Z4 E18706.915978 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.01269 matz1=4 note=collision lift
G1 X62.114524 Y125.971951 Z4 E18711.256429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X62.664296 Y126.88919 Z4 E18715.702398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.121515 Y127.855899 Z4 E18720.148367 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.481779 Y128.862768 Z4 E18724.594336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.741617 Y129.900101 Z4 E18729.040305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.898528 Y130.957907 Z4 E18733.486274 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.951 Y132.026 Z4 E18737.932244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.898528 Y133.094093 Z4 E18742.378213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.741617 Y134.151899 Z4 E18746.824182 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.481779 Y135.189232 Z4 E18751.270151 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X63.121515 Y136.196101 Z4 E18755.71612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X62.664296 Y137.16281 Z4 E18760.162089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X62.114524 Y138.080049 Z4 E18764.608058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X61.477495 Y138.938984 Z4 E18769.054027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X60.759343 Y139.731343 Z4 E18773.499997 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X60.5975 Y139.878029 Z4 E18774.408107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X59.966984 Y140.449495 Z4.425477 E18778.363553 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4 matz1=4.425477 note=collision lift
G1 X59.108049 Y141.086524 Z4.960168 E18783.334298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.425477 matz1=4.960168 note=collision lift
G1 X58.835422 Y141.24993 Z5.119091 E18784.811729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.960168 matz1=5.119091 note=collision lift
G1 X58.19081 Y141.636296 Z5.494858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.119091 matz1=5.494858 note=collision lift
G1 X57.306184 Y142.054693 Z5.984149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.494858 matz1=5.984149 note=collision lift
G1 X57.224101 Y142.093515 Z6.074949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=5.984149 matz1=6 note=collision lift
G1 X56.217232 Y142.453779 Z7.14433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X56.098007 Y142.483643 Z7.267238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X55.179899 Y142.713617 Z7.267238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X54.878559 Y142.758317 Z7.267238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0016
G0 X54.878559 Y142.758317 Z11.267238 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0015 note=intra-page lift
G0 X58.19081 Y165.087704 Z11.267238 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0015 note=intra-page XY
G0 X58.19081 Y165.087704 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0015 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0015
G1 X58.505635 Y165.276403 Z6 E18784.830399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X58.505775 Y165.276487 Z6.000888 E18784.830491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X58.507298 Y165.2774 Z6 E18784.830694 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X59.108049 Y165.637476 Z6 E18784.970491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X59.453163 Y165.89343 Z6 E18785.123543 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X59.966984 Y166.274505 Z6 E18785.446216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X60.604416 Y166.85224 Z6 E18786.058984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X60.759343 Y166.992657 Z6 E18786.238903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X61.127904 Y167.399302 Z6 E18786.768791 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X61.128233 Y167.399665 Z6.000261 E18786.76937 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X61.477495 Y167.785016 Z5.740223 E18787.421949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=5.740223 note=collision lift
G1 X61.562785 Y167.900016 Z5.668635 E18787.618053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.740223 matz1=5.668635 note=collision lift
G1 X62.114524 Y168.643951 Z5.205533 E18789.058228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.668635 matz1=5.205533 note=collision lift
G1 X62.328101 Y169.000282 Z4.997815 E18789.800749 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.205533 matz1=4.997815 note=collision lift
G1 X62.664296 Y169.56119 Z4.670842 E18791.090709 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.997815 matz1=4.670842 note=collision lift
G1 X62.958324 Y170.182859 Z4.326994 E18792.607073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.670842 matz1=4.326994 note=collision lift
G1 X63.121515 Y170.527899 Z4.136152 E18793.519394 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.326994 matz1=4.136152 note=collision lift
G1 X63.152116 Y170.613421 Z4.090736 E18793.743939 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.136152 matz1=4.090736 note=collision lift
G1 X63.444914 Y171.431739 Z4.525297 E18796.037024 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.090736 matz1=4.525297 note=collision lift
G1 X63.481779 Y171.534768 Z4.58001 E18796.344281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.525297 matz1=4.58001 note=collision lift
G1 X63.741617 Y172.572101 Z5.114701 E18799.565371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.58001 matz1=5.114701 note=collision lift
G1 X63.741631 Y172.572193 Z5.114747 E18799.56567 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X63.76551 Y172.733173 Z5.196118 E18800.090603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.114747 matz1=5.196118 note=collision lift
G1 X63.898528 Y173.629907 Z5.649391 E18803.182664 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.196118 matz1=5.649391 note=collision lift
G1 X63.919877 Y174.064478 Z5.866937 E18804.76781 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.649391 matz1=5.866643 note=collision lift
G1 X63.932982 Y174.331234 Z6.000475 E18805.77332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.866643 matz1=6 note=collision lift
G1 X63.933029 Y174.332183 Z6 E18805.776939 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X63.951 Y174.698 Z6 E18807.044131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X63.910074 Y175.531073 Z6 E18810.068644 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X63.898528 Y175.766093 Z6 E18810.956765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X63.741617 Y176.823899 Z6 E18815.186362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X63.694159 Y177.013362 Z6 E18815.993105 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X63.481779 Y177.861232 Z6 E18819.627044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X63.121515 Y178.868101 Z6 E18824.073013 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X62.664296 Y179.83481 Z6 E18828.518982 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X62.476001 Y180.148961 Z6 E18830.041709 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X62.475513 Y180.149775 Z6.000475 E18830.046123 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X62.114524 Y180.752049 Z5.649391 E18833.309989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=5.649391 note=collision lift
G1 X61.477551 Y181.610908 Z5.114747 E18838.280298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X61.477495 Y181.610984 Z5.114701 E18838.280733 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X60.759343 Y182.403343 Z4.58001 E18843.251478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X59.966984 Y183.121495 Z4.04532 E18848.222222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X59.894181 Y183.175489 Z4 E18848.643536 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.04532 matz1=4 note=collision lift
G1 X59.108049 Y183.758524 Z4 E18852.712671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X58.19081 Y184.308296 Z4 E18857.15864 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X57.224101 Y184.765515 Z4 E18861.604609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X56.217232 Y185.125779 Z4 E18866.050578 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X55.179899 Y185.385617 Z4 E18870.496547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X54.122093 Y185.542528 Z4 E18874.942516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X53.054 Y185.595 Z4 E18879.388485 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X51.985907 Y185.542528 Z4 E18883.834455 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X50.928101 Y185.385617 Z4 E18888.280424 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X49.890768 Y185.125779 Z4 E18892.726393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X48.883899 Y184.765515 Z4 E18897.172362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X47.91719 Y184.308296 Z4 E18901.618331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X46.999951 Y183.758524 Z4 E18906.0643 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X46.141016 Y183.121495 Z4 E18910.510269 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X45.348657 Y182.403343 Z4 E18914.956238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X44.630505 Y181.610984 Z4 E18919.402208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X43.993476 Y180.752049 Z4 E18923.848177 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X43.443704 Y179.83481 Z4 E18928.294146 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.986485 Y178.868101 Z4 E18932.740115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.626221 Y177.861232 Z4 E18937.186084 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.366383 Y176.823899 Z4 E18941.632053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.209472 Y175.766093 Z4 E18946.078022 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.157 Y174.698 Z4 E18950.523991 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.209472 Y173.629907 Z4 E18954.969961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.366383 Y172.572101 Z4 E18959.41593 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.626221 Y171.534768 Z4 E18963.861899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X42.986485 Y170.527899 Z4 E18968.307868 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X43.443704 Y169.56119 Z4 E18972.753837 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X43.993476 Y168.643951 Z4 E18977.199806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X44.630505 Y167.785016 Z4 E18981.645775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X45.348657 Y166.992657 Z4 E18986.091744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X46.141016 Y166.274505 Z4 E18990.537713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X46.999951 Y165.637476 Z4 E18994.983683 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X47.91719 Y165.087704 Z4 E18999.429652 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X48.801962 Y164.669238 Z4 E19003.498786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X48.883899 Y164.630485 Z4.04532 E19003.9201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4 matz1=4.04532 note=collision lift
G1 X49.890768 Y164.270221 Z4.58001 E19008.890845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.04532 matz1=4.58001 note=collision lift
G1 X50.928101 Y164.010383 Z5.114701 E19013.861589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.58001 matz1=5.114701 note=collision lift
G1 X50.928193 Y164.010369 Z5.114747 E19013.862025 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X51.985907 Y163.853472 Z5.649391 E19018.832334 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.114747 matz1=5.649391 note=collision lift
G1 X52.687234 Y163.819018 Z6.000475 E19022.0962 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.649391 matz1=6 note=collision lift
G1 X52.688183 Y163.818971 Z6 E19022.100614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y163.801 Z6 E19023.62334 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X53.40052 Y163.818023 Z6 E19025.065741 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X54.122093 Y163.853472 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X55.179899 Y164.010383 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X56.217232 Y164.270221 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X57.048436 Y164.567631 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X57.04857 Y164.567679 Z6.000071 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X57.048704 Y164.567727 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X57.224101 Y164.630485 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X58.19081 Y165.087704 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0015
G0 X58.19081 Y165.087704 Z10 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0014 note=intra-page lift
G0 X63.951 Y153.362 Z10 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0014 note=intra-page XY
G0 X63.951 Y153.362 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0014 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0014
G1 X63.898528 Y154.430093 Z4 E19025.224222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X63.835343 Y154.856051 Z4 E19025.377555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X63.741617 Y155.487899 Z4 E19025.699666 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X63.532353 Y156.323327 Z4 E19026.312996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X63.481779 Y156.525232 Z4 E19026.492072 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X63.121515 Y157.532101 Z4 E19027.60144 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X63.026394 Y157.733218 Z4 E19027.872065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X62.956298 Y157.881425 Z4 E19028.080275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X62.664296 Y158.49881 Z4.341478 E19029.148137 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4 matz1=4.341478 note=collision lift
G1 X62.401052 Y158.938006 Z4.597501 E19030.054762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.341478 matz1=4.597501 note=collision lift
G1 X62.114524 Y159.416049 Z4.876169 E19031.144825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.597501 matz1=4.876169 note=collision lift
G1 X61.647315 Y160.046008 Z5.268321 E19032.861085 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.876169 matz1=5.268321 note=collision lift
G1 X61.477495 Y160.274984 Z5.410859 E19033.537716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.268321 matz1=5.410859 note=collision lift
G1 X60.76795 Y161.057846 Z5.939141 E19036.291037 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.410859 matz1=5.939141 note=collision lift
G1 X60.759343 Y161.067343 Z5.94555 E19036.326809 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.939141 matz1=5.94555 note=collision lift
G1 X59.966984 Y161.785495 Z6.48024 E19039.512106 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.94555 matz1=6 note=collision lift
G1 X59.758597 Y161.940045 Z6.609962 E19040.344616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X59.108049 Y162.422524 Z7.014931 E19043.093606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X58.651992 Y162.695875 Z7.280782 E19045.021822 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X58.19081 Y162.972296 Z7.549621 E19047.071308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X57.464036 Y163.316035 Z7.951603 E19050.322656 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X57.376535 Y163.35742 Z8 E19050.729213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X57.224101 Y163.429515 Z8 E19051.369158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X56.217232 Y163.789779 Z8 E19055.611067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X56.068064 Y163.827143 Z8 E19056.247118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X55.179899 Y164.049617 Z8 E19060.053759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X54.122093 Y164.206528 Z8 E19064.499728 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y164.259 Z8 E19068.945697 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y164.206528 Z8 E19073.391666 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X51.478006 Y164.131188 Z8 E19075.526378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X51.476795 Y164.131008 Z8 E19075.531468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y164.049617 Z7.737636 E19078.082589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X50.91586 Y164.046551 Z7.731326 E19078.141246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X50.750661 Y164.005171 Z7.652265 E19078.921861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X50.744973 Y164.003746 Z7.655196 E19078.949115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y163.789779 Z7.220833 E19083.031365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y163.429515 Z6.686142 E19088.00211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y162.972296 Z6.151452 E19092.972854 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X46.999951 Y162.422524 Z5.616761 E19097.943599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=5.616761 note=collision lift
G1 X46.141016 Y161.785495 Z5.082071 E19102.914344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X45.348657 Y161.067343 Z4.547381 E19107.885088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X44.630505 Y160.274984 Z4.01269 E19112.855833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X44.615386 Y160.254598 Z4 E19112.973806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.01269 matz1=4 note=collision lift
G1 X43.993476 Y159.416049 Z4 E19117.314257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X43.443704 Y158.49881 Z4 E19121.760226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.986485 Y157.532101 Z4 E19126.206195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.626221 Y156.525232 Z4 E19130.652164 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.366383 Y155.487899 Z4 E19135.098133 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.209472 Y154.430093 Z4 E19139.544102 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.157 Y153.362 Z4 E19143.990071 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.209472 Y152.293907 Z4 E19148.43604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.366383 Y151.236101 Z4 E19152.88201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.626221 Y150.198768 Z4 E19157.327979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X42.986485 Y149.191899 Z4 E19161.773948 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X43.151702 Y148.842575 Z4 E19163.380514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X43.443704 Y148.22519 Z4.341478 E19166.555063 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4 matz1=4.341478 note=collision lift
G1 X43.993476 Y147.307951 Z4.876169 E19171.525808 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X44.630505 Y146.449016 Z5.410859 E19176.496552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X45.348657 Y145.656657 Z5.94555 E19181.467297 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X46.141016 Y144.938505 Z6.48024 E19186.438041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.94555 matz1=6 note=collision lift
G1 X46.999951 Y144.301476 Z7.014931 E19191.408786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X47.91719 Y143.751704 Z7.549621 E19196.379531 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X48.731465 Y143.36658 Z8 E19200.566475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X48.883899 Y143.294485 Z8 E19201.267527 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X49.890768 Y142.934221 Z8 E19205.713496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X50.928101 Y142.674383 Z8 E19210.159465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X51.985907 Y142.517472 Z8 E19214.605434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X53.054 Y142.465 Z8 E19219.051404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X54.122093 Y142.517472 Z8 E19223.497373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X54.629994 Y142.592812 Z8 E19225.632085 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X54.631205 Y142.592992 Z8 E19225.637174 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X54.632482 Y142.593181 Z8 E19225.642542 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X55.179899 Y142.674383 Z8 E19227.943342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X56.217232 Y142.934221 Z8 E19232.389311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X57.224101 Y143.294485 Z8 E19236.83528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X57.376535 Y143.36658 Z8 E19237.536332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X58.19081 Y143.751704 Z7.549621 E19241.723277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X59.108049 Y144.301476 Z7.014931 E19246.694021 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X59.966984 Y144.938505 Z6.48024 E19251.664766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X60.759343 Y145.656657 Z5.94555 E19256.63551 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=5.94555 note=collision lift
G1 X61.477495 Y146.449016 Z5.410859 E19261.606255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.94555 matz1=5.410859 note=collision lift
G1 X62.114524 Y147.307951 Z4.876169 E19266.577 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.410859 matz1=4.876169 note=collision lift
G1 X62.664296 Y148.22519 Z4.341478 E19271.547744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.876169 matz1=4.341478 note=collision lift
G1 X62.827786 Y148.570859 Z4.150287 E19273.325152 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.341478 matz1=4.150287 note=collision lift
G1 X62.956298 Y148.842575 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.150287 matz1=4 note=collision lift
G1 X63.121515 Y149.191899 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X63.481779 Y150.198768 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X63.741617 Y151.236101 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X63.898528 Y152.293907 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X63.951 Y153.362 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0014
G0 X63.951 Y153.362 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0013 note=intra-page lift
G0 X80.134328 Y152.622922 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0013 note=intra-page XY
G0 X80.134328 Y152.622922 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0013 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0013
G1 X79.343476 Y152.236459 Z4 E19273.432526 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X78.82051 Y151.903857 Z4 E19273.636965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X78.590369 Y151.75749 Z4 E19273.760667 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X77.656977 Y150.960657 Z4 E19274.572407 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X77.19 Y150.562 Z4 E19275.135195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X76.614738 Y149.888152 Z4 E19276.131475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X75.99451 Y149.161631 Z4 E19277.449385 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X75.702173 Y148.701975 Z4 E19278.314172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X75.515541 Y148.408524 Z4 E19278.909279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X75.129078 Y147.617672 Z4 E19280.565324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X75.041072 Y147.360301 Z4 E19281.120496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X74.845114 Y146.787228 Z4 E19282.430331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X74.673639 Y145.915346 Z4 E19284.536071 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X74.67333 Y145.909589 Z4 E19284.550447 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X74.624645 Y145.000177 Z4 E19286.937175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X74.67568 Y144.413105 Z4 E19288.604026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X74.708125 Y144.039875 Z4 E19289.713772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X74.93407 Y143.032593 Z4 E19292.972948 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X74.965455 Y142.944996 Z4 E19293.281233 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X75.312471 Y141.976482 Z4 E19296.849732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X75.519349 Y141.55313 Z4 E19298.582067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X75.85332 Y140.869698 Z4 E19301.508499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X76.24075 Y140.240009 Z4 E19304.506528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X76.566609 Y139.710391 Z4 E19307.09182 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X77.46233 Y138.496715 Z4 E19313.363094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X78.550475 Y137.226822 Z4 E19320.31583 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X79.841034 Y135.898866 Z4 E19328.014548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X81.344 Y134.511 Z4 E19336.519775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X82.557973 Y132.980941 Z4 E19344.640044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X84.545219 Y130.913906 Z4 E19356.561162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X87.272855 Y128.48223 Z4 E19371.753487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X90.708 Y125.85825 Z4 E19389.725068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X92.680612 Y124.528 Z4 E19399.616779 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X94.81777 Y123.214301 Z4 E19410.046472 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X97.115363 Y121.938693 Z4 E19420.97221 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X99.569281 Y120.722719 Z4 E19432.358273 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X102.175415 Y119.58792 Z4 E19444.175936 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X104.929652 Y118.55584 Z4 E19456.404278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X107.827884 Y117.648019 Z4 E19469.031011 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X110.866 Y116.886 Z4 E19482.053281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X110.103981 Y119.924116 Z4 E19495.07555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X109.19616 Y122.822348 Z4 E19507.702284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X108.16408 Y125.576585 Z4 E19519.930626 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X107.029281 Y128.182719 Z4 E19531.748289 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X105.813307 Y130.636637 Z4 E19543.134352 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X104.537699 Y132.93423 Z4 E19554.06009 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X103.224 Y135.071388 Z4 E19564.489782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X101.89375 Y137.044 Z4 E19574.381494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X99.26977 Y140.479145 Z4 E19592.353075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X96.838094 Y143.206781 Z4 E19607.5454 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X94.771059 Y145.194027 Z4 E19619.466518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X93.241 Y146.408 Z4 E19627.586787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X91.853134 Y147.910966 Z4 E19636.092014 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X90.525178 Y149.201525 Z4 E19643.790732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X89.255285 Y150.28967 Z4 E19650.743468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X88.041609 Y151.185391 Z4 E19657.014742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X86.882302 Y151.89868 Z4 E19662.673815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X85.775518 Y152.439529 Z4 E19667.795313 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X85.021641 Y152.709641 Z4 E19671.124676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X84.719407 Y152.81793 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
G1 X83.712125 Y153.043875 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
G1 X82.751823 Y153.127355 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
G1 X81.836654 Y153.078361 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
G1 X80.964772 Y152.906886 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
G1 X80.134328 Y152.622922 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0013
G0 X80.134328 Y152.622922 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0012 note=intra-page lift
G0 X76.92773 Y161.567686 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0012 note=intra-page XY
G0 X76.92773 Y161.567686 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0012 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0012
G1 X75.956445 Y162.364798 Z4 E19671.34347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X75.741694 Y162.479585 Z4 E19671.43649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X74.639048 Y163.068962 Z4 E19672.172928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X74.400078 Y163.141453 Z4 E19672.371931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X73.209588 Y163.502584 Z4 E19673.620854 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X72.954879 Y163.52767 Z4 E19673.931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X71.723 Y163.649 Z4 E19675.687247 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X71.462102 Y163.623304 Z4 E19676.113696 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X70.236412 Y163.502584 Z4 E19678.372107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X69.979589 Y163.424678 Z4 E19678.92002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X68.806952 Y163.068962 Z4 E19681.675435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X68.564779 Y162.939518 Z4 E19682.349971 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X67.489555 Y162.364798 Z4 E19685.59723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X67.272481 Y162.18665 Z4 E19686.40355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X66.334846 Y161.417154 Z4 E19690.137492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X66.152753 Y161.195273 Z4 E19691.080757 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X65.387202 Y160.262445 Z4 E19695.296221 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X65.248963 Y160.003818 Z4 E19696.381591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X64.683038 Y158.945048 Z4 E19701.073418 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X64.596106 Y158.65847 Z4 E19702.306052 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X64.249416 Y157.515588 Z4 E19707.27141 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X64.103 Y156.029 Z4 E19713.481831 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X64.249416 Y154.542412 Z4 E19719.692252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X64.683038 Y153.112952 Z4 E19725.902672 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X65.387202 Y151.795555 Z4 E19732.113093 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X66.334846 Y150.640846 Z4 E19738.323513 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X67.489555 Y149.693202 Z4 E19744.533934 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X68.806952 Y148.989038 Z4 E19750.744355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X70.236412 Y148.555416 Z4 E19756.954775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X71.723 Y148.409 Z4 E19763.165196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X73.209588 Y148.555416 Z4 E19769.375617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X74.639048 Y148.989038 Z4 E19775.586037 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X75.956445 Y149.693202 Z4 E19781.796458 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X77.111154 Y150.640846 Z4 E19788.006878 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X78.058798 Y151.795555 Z4 E19794.217299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X78.762962 Y153.112952 Z4 E19800.42772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X79.196584 Y154.542412 Z4 E19806.63814 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X79.343 Y156.029 Z4 E19812.848561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X79.224163 Y157.235572 Z4 E19817.889175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X79.196584 Y157.515588 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=end-early tail
G1 X78.762962 Y158.945048 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=end-early tail
G1 X78.058798 Y160.262445 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=end-early tail
G1 X77.111154 Y161.417154 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=end-early tail
G1 X76.92773 Y161.567686 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0012
G0 X76.92773 Y161.567686 Z8.24769 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0011 note=intra-page lift
G0 X84.593819 Y170.908842 Z8.24769 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0011 note=intra-page XY
G0 X84.593819 Y170.908842 Z4.24769 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0011 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0011
G1 X84.693985 Y171.188788 Z4.395888 E19817.90447 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.24769 matz1=4.395888 note=collision lift
G1 X84.69407 Y171.189025 Z4.396223 E19817.904509 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.395888 matz1=4.396223 note=collision lift
G1 X84.817612 Y171.534301 Z4.579577 E19817.965604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.396223 matz1=4.579577 note=collision lift
G1 X84.817779 Y171.534768 Z4.58001 E19817.965739 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.579577 matz1=4.58001 note=collision lift
G1 X84.982234 Y172.19131 Z4.918421 E19818.200989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.58001 matz1=4.918421 note=collision lift
G1 X84.988393 Y172.215897 Z4.931094 E19818.212882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.918421 matz1=4.931094 note=collision lift
G1 X84.988437 Y172.216072 Z4.931004 E19818.212967 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.931094 matz1=4.931004 note=collision lift
G1 X85.077303 Y172.570846 Z5.113869 E19818.409375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.931004 matz1=5.113869 note=collision lift
G1 X85.077617 Y172.572101 Z5.114701 E19818.410201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.113869 matz1=5.114701 note=collision lift
G1 X85.180647 Y173.266673 Z5.465784 E19818.917516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.114701 matz1=5.465784 note=collision lift
G1 X85.180674 Y173.266852 Z5.465694 E19818.917668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.465784 matz1=5.465694 note=collision lift
G1 X85.216865 Y173.510835 Z5.58902 E19819.13643 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.465694 matz1=5.58902 note=collision lift
G1 X85.234221 Y173.627838 Z5.64816 E19819.248815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.58902 matz1=5.64816 note=collision lift
G1 X85.234528 Y173.629907 Z5.649391 E19819.250923 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.64816 matz1=5.649391 note=collision lift
G1 X85.268982 Y174.331234 Z6.000475 E19820.018409 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.649391 matz1=6 note=collision lift
G1 X85.269029 Y174.332183 Z6 E19820.019563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X85.287 Y174.698 Z6 E19820.436172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X85.276551 Y174.9107 Z6 E19820.695499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X85.234528 Y175.766093 Z6 E19821.865324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X85.140096 Y176.402703 Z6 E19822.878195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X85.077617 Y176.823899 Z6 E19823.611438 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X84.817779 Y177.861232 Z6 E19825.674515 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X84.816157 Y177.865765 Z6 E19825.684519 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X84.457515 Y178.868101 Z6 E19828.054553 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X84.271344 Y179.261728 Z6 E19829.114471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X84.000296 Y179.83481 Z6 E19830.751554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X83.812001 Y180.148961 Z6 E19831.748136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X83.811513 Y180.149775 Z6.000475 E19831.751079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X83.582182 Y180.532391 Z5.777436 E19833.16805 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=5.777263 note=collision lift
G1 X83.450524 Y180.752049 Z5.649391 E19834.012675 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.777263 matz1=5.649391 note=collision lift
G1 X82.813551 Y181.610908 Z5.114747 E19837.784832 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X82.813495 Y181.610984 Z5.114701 E19837.785179 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X82.802637 Y181.622963 Z5.106617 E19837.845256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.114701 matz1=5.106617 note=collision lift
G1 X82.095343 Y182.403343 Z4.58001 E19841.953886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.106617 matz1=4.58001 note=collision lift
G1 X81.881632 Y182.597039 Z4.435796 E19843.14609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.58001 matz1=4.435796 note=collision lift
G1 X81.302984 Y183.121495 Z4.04532 E19846.518796 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.435796 matz1=4.04532 note=collision lift
G1 X81.230181 Y183.175489 Z4 E19846.923926 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.04532 matz1=4 note=collision lift
G1 X80.808072 Y183.488547 Z4 E19849.070552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X80.444049 Y183.758524 Z4 E19850.954786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X79.52681 Y184.308296 Z4 E19855.400755 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X78.560101 Y184.765515 Z4 E19859.846724 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X77.553232 Y185.125779 Z4 E19864.292694 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X76.515899 Y185.385617 Z4 E19868.738663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X75.458093 Y185.542528 Z4 E19873.184632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X74.39 Y185.595 Z4 E19877.630601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X73.321907 Y185.542528 Z4 E19882.07657 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X72.264101 Y185.385617 Z4 E19886.522539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X71.226768 Y185.125779 Z4 E19890.968508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X70.219899 Y184.765515 Z4 E19895.414477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X69.870575 Y184.600298 Z4 E19897.021043 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X69.25319 Y184.308296 Z4.341478 E19900.195593 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4 matz1=4.341478 note=collision lift
G1 X68.335951 Y183.758524 Z4.876169 E19905.166337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X67.477016 Y183.121495 Z5.410859 E19910.137082 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X66.684657 Y182.403343 Z5.94555 E19915.107826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X65.966505 Y181.610984 Z6.48024 E19920.078571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.94555 matz1=6 note=collision lift
G1 X65.329476 Y180.752049 Z7.014931 E19925.049316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X64.779704 Y179.83481 Z7.549621 E19930.02006 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X64.39458 Y179.020535 Z8 E19934.207005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X64.322485 Y178.868101 Z8 E19934.908057 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.962221 Y177.861232 Z8 E19939.354026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.702383 Y176.823899 Z8 E19943.799995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.545472 Y175.766093 Z8 E19948.245964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.493 Y174.698 Z8 E19952.691933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.545472 Y173.629907 Z8 E19957.137902 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.620812 Y173.122006 Z8 E19959.272614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.620992 Y173.120795 Z8 E19959.277704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.702383 Y172.572101 Z7.737636 E19961.828825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.705449 Y172.55986 Z7.731326 E19961.887482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.746829 Y172.394661 Z7.652265 E19962.668097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.748254 Y172.388973 Z7.655196 E19962.695351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X63.962221 Y171.534768 Z7.220833 E19966.777601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X64.322485 Y170.527899 Z6.686142 E19971.748346 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X64.779704 Y169.56119 Z6.151452 E19976.719091 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X65.329476 Y168.643951 Z5.616761 E19981.689835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=5.616761 note=collision lift
G1 X65.966505 Y167.785016 Z5.082071 E19986.66058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X66.684657 Y166.992657 Z4.547381 E19991.631324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X67.477016 Y166.274505 Z4.01269 E19996.602069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X67.497402 Y166.259386 Z4 E19996.720042 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.01269 matz1=4 note=collision lift
G1 X68.335951 Y165.637476 Z4 E20001.060493 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X69.25319 Y165.087704 Z4 E20005.506462 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X70.219899 Y164.630485 Z4 E20009.952431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X71.226768 Y164.270221 Z4 E20014.3984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X72.264101 Y164.010383 Z4 E20018.844369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X73.321907 Y163.853472 Z4 E20023.290338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X74.39 Y163.801 Z4 E20027.736308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X75.458093 Y163.853472 Z4 E20032.182277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X76.515899 Y164.010383 Z4 E20036.628246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X77.553232 Y164.270221 Z4 E20041.074215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X78.560101 Y164.630485 Z4 E20045.520184 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X79.52681 Y165.087704 Z4 E20049.966153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X80.444049 Y165.637476 Z4 E20054.412122 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X81.302984 Y166.274505 Z4 E20058.858091 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X81.306478 Y166.277672 Z4 E20058.877697 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X82.095343 Y166.992657 Z4.532333 E20063.826522 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4 matz1=4.532333 note=collision lift
G1 X82.201226 Y167.109482 Z4.611167 E20064.559402 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.532333 matz1=4.611167 note=collision lift
G1 X82.813495 Y167.785016 Z5.067023 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.611167 matz1=5.067023 note=collision lift
G1 X83.450524 Y168.643951 Z5.601713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.067023 matz1=5.601713 note=collision lift
G1 X84.000296 Y169.56119 Z6.136404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.601713 matz1=6 note=collision lift
G1 X84.095494 Y169.762469 Z6.247732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X84.418637 Y170.445698 Z5.869835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=5.869835 note=collision lift
G1 X84.457515 Y170.527899 Z5.869835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.869835 matz1=5.869835 note=collision lift
G1 X84.593819 Y170.908842 Z5.869835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.869835 matz1=5.869835 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0011
G0 X84.593819 Y170.908842 Z9.869835 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0010 note=intra-page lift
G0 X100.86281 Y165.087704 Z9.869835 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0010 note=intra-page XY
G0 X100.86281 Y165.087704 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0010 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0010
G1 X101.780049 Y165.637476 Z4 E20064.717883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X102.125925 Y165.893995 Z4 E20064.871215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X102.638984 Y166.274505 Z4 E20065.193326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X103.277119 Y166.852877 Z4 E20065.806657 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X103.431343 Y166.992657 Z4 E20065.985732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X104.149495 Y167.785016 Z4 E20067.0951 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X104.282024 Y167.963711 Z4 E20067.365725 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X104.786524 Y168.643951 Z4 E20068.52143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X105.122283 Y169.20413 Z4 E20069.548422 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X105.336296 Y169.56119 Z4 E20070.264723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X105.754762 Y170.445962 Z4 E20072.138059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X105.793515 Y170.527899 Z4.04532 E20072.347191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4 matz1=4.04532 note=collision lift
G1 X105.794611 Y170.53096 Z4.046945 E20072.354746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.04532 matz1=4.046945 note=collision lift
G1 X106.153779 Y171.534768 Z4.58001 E20075.02946 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.046945 matz1=4.58001 note=collision lift
G1 X106.220723 Y171.802022 Z4.717766 E20075.784697 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.58001 matz1=4.717766 note=collision lift
G1 X106.413617 Y172.572101 Z5.114701 E20078.107932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.717766 matz1=5.114701 note=collision lift
G1 X106.413631 Y172.572193 Z5.114747 E20078.108219 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X106.493992 Y173.113943 Z5.388586 E20079.838276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.114747 matz1=5.388586 note=collision lift
G1 X106.570528 Y173.629907 Z5.649391 E20081.582607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.388586 matz1=5.649391 note=collision lift
G1 X106.604982 Y174.331234 Z6.000475 E20084.079617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.649391 matz1=6 note=collision lift
G1 X106.605029 Y174.332183 Z6 E20084.083109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X106.611442 Y174.462734 Z6 E20084.515483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X106.623 Y174.698 Z6 E20085.306612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X106.570528 Y175.766093 Z6 E20089.091685 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X106.541905 Y175.959051 Z6 E20089.816317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X106.413617 Y176.823899 Z6 E20093.19372 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X106.261587 Y177.430837 Z6 E20095.740778 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X106.153779 Y177.861232 Z6 E20097.585435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X105.793515 Y178.868101 Z6 E20102.031405 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X105.336296 Y179.83481 Z6 E20106.477374 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X105.148001 Y180.148961 Z6 E20108.0001 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X105.147513 Y180.149775 Z6.000475 E20108.004514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X104.786524 Y180.752049 Z5.649391 E20111.26838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=5.649391 note=collision lift
G1 X104.149551 Y181.610908 Z5.114747 E20116.238689 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X104.149495 Y181.610984 Z5.114701 E20116.239125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X103.431343 Y182.403343 Z4.58001 E20121.209869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X102.638984 Y183.121495 Z4.04532 E20126.180614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X102.566181 Y183.175489 Z4 E20126.601928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.04532 matz1=4 note=collision lift
G1 X101.780049 Y183.758524 Z4 E20130.671062 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X100.86281 Y184.308296 Z4 E20135.117031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X99.896101 Y184.765515 Z4 E20139.563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X98.889232 Y185.125779 Z4 E20144.00897 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X97.851899 Y185.385617 Z4 E20148.454939 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X96.794093 Y185.542528 Z4 E20152.900908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X95.726 Y185.595 Z4 E20157.346877 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X94.657907 Y185.542528 Z4 E20161.792846 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X93.600101 Y185.385617 Z4 E20166.238815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X92.562768 Y185.125779 Z4 E20170.684784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X91.555899 Y184.765515 Z4 E20175.130753 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X91.206575 Y184.600298 Z4 E20176.737319 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X90.58919 Y184.308296 Z4.341478 E20179.911869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4 matz1=4.341478 note=collision lift
G1 X89.671951 Y183.758524 Z4.876169 E20184.882613 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X88.813016 Y183.121495 Z5.410859 E20189.853358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X88.020657 Y182.403343 Z5.94555 E20194.824102 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X87.302505 Y181.610984 Z6.48024 E20199.794847 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.94555 matz1=6 note=collision lift
G1 X86.665476 Y180.752049 Z7.014931 E20204.765592 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X86.115704 Y179.83481 Z7.549621 E20209.736336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.73058 Y179.020535 Z8 E20213.923281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.658485 Y178.868101 Z8 E20214.624333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.298221 Y177.861232 Z8 E20219.070302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.038383 Y176.823899 Z8 E20223.516271 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X84.881472 Y175.766093 Z8 E20227.96224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X84.829 Y174.698 Z8 E20232.408209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X84.881472 Y173.629907 Z8 E20236.854178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X84.956812 Y173.122006 Z8 E20238.98889 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X84.956992 Y173.120795 Z8 E20238.99398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.038383 Y172.572101 Z7.737636 E20241.545101 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.041449 Y172.55986 Z7.731326 E20241.603758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.07747 Y172.416054 Z7.662503 E20242.283283 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.178226 Y172.013817 Z7.869835 E20244.210744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.298221 Y171.534768 Z7.869835 E20246.263929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.419066 Y171.197028 Z7.869835 E20247.755265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.420372 Y171.19338 Z7.871773 E20247.773277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.543114 Y170.850337 Z7.885172 E20249.289053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.543842 Y170.848303 Z7.886252 E20249.299096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.658485 Y170.527899 Z7.877315 E20250.714372 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.664091 Y170.516045 Z7.870759 E20250.775325 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.666986 Y170.509924 Z7.869872 E20250.803715 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.667017 Y170.509858 Z7.869835 E20250.804055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X85.73058 Y170.375465 Z7.869835 E20251.422135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X86.115704 Y169.56119 Z7.419456 E20255.60908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X86.665476 Y168.643951 Z6.884766 E20260.579824 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X87.302505 Y167.785016 Z6.350075 E20265.550569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X88.020657 Y166.992657 Z5.815385 E20270.521314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=5.815385 note=collision lift
G1 X88.813016 Y166.274505 Z5.280694 E20275.492058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.815385 matz1=5.280694 note=collision lift
G1 X89.671951 Y165.637476 Z4.746004 E20280.462803 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.280694 matz1=4.746004 note=collision lift
G1 X90.58919 Y165.087704 Z4.211314 E20285.433547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.746004 matz1=4.211314 note=collision lift
G1 X90.97124 Y164.907008 Z4 E20287.398022 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.211314 matz1=4 note=collision lift
G1 X91.555899 Y164.630485 Z4 E20290.086912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X92.562768 Y164.270221 Z4 E20294.532881 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X93.600101 Y164.010383 Z4 E20298.97885 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X94.657907 Y163.853472 Z4 E20303.424819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X95.726 Y163.801 Z4 E20307.870788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X96.072487 Y163.818022 Z4 E20309.313049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X96.794093 Y163.853472 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=end-early tail
G1 X97.851899 Y164.010383 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=end-early tail
G1 X98.889232 Y164.270221 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=end-early tail
G1 X99.896101 Y164.630485 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=end-early tail
G1 X100.86281 Y165.087704 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0010
G0 X100.86281 Y165.087704 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0009 note=intra-page lift
G0 X107.11061 Y154.26735 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0009 note=intra-page XY
G0 X107.11061 Y154.26735 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0009 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0009
G1 X107.067798 Y154.347445 Z4 E20309.314192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X106.173823 Y155.436757 Z4 E20309.624863 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X106.120154 Y155.502154 Z4 E20309.661028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X105.026035 Y156.400074 Z4 E20310.560304 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X104.965445 Y156.449798 Z4 E20310.62633 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X103.711689 Y157.119945 Z4 E20312.119373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X103.648048 Y157.153962 Z4 E20312.2101 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X102.281692 Y157.568441 Z4 E20314.30207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X102.218588 Y157.587584 Z4 E20314.412337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X100.791437 Y157.728146 Z4 E20317.108393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X100.732 Y157.734 Z4 E20317.233042 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X99.29866 Y157.592828 Z4 E20320.538345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X99.245412 Y157.587584 Z4 E20320.672213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X97.861203 Y157.167689 Z4 E20324.591924 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X97.815952 Y157.153962 Z4 E20324.729852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X96.534774 Y156.469158 Z4 E20329.26913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X96.498555 Y156.449798 Z4 E20329.405959 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X95.370786 Y155.524262 Z4 E20334.569964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X95.343846 Y155.502154 Z4 E20334.700533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X94.414365 Y154.369577 Z4 E20340.494426 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X94.396202 Y154.347445 Z4 E20340.61346 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X93.692038 Y153.030048 Z4 E20346.823881 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X93.258416 Y151.600588 Z4 E20353.034301 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X93.112 Y150.114 Z4 E20359.244722 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X93.258416 Y148.627412 Z4 E20365.455143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X93.692038 Y147.197952 Z4 E20371.665563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X94.396202 Y145.880555 Z4 E20377.875984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X95.343846 Y144.725846 Z4 E20384.086404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X96.498555 Y143.778202 Z4 E20390.296825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X97.815952 Y143.074038 Z4 E20396.507246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X99.245412 Y142.640416 Z4 E20402.717666 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X100.732 Y142.494 Z4 E20408.928087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X102.218588 Y142.640416 Z4 E20415.138508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X103.648048 Y143.074038 Z4 E20421.348928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X104.965445 Y143.778202 Z4 E20427.559349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X106.120154 Y144.725846 Z4 E20433.769769 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X107.067798 Y145.880555 Z4 E20439.98019 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X107.771962 Y147.197952 Z4 E20446.190611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X108.205584 Y148.627412 Z4 E20452.401031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X108.292261 Y149.50746 Z4 E20456.077549 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X108.352 Y150.114 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X108.205584 Y151.600588 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X107.771962 Y153.030048 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X107.11061 Y154.26735 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0009
G0 X107.11061 Y154.26735 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0008 note=intra-page lift
G0 X122.089446 Y162.273704 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0008 note=intra-page XY
G0 X122.089446 Y162.273704 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0008 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0008
G1 X121.388888 Y162.710212 Z4 E20456.171968 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X120.774924 Y162.989686 Z4 E20456.389362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X120.600922 Y163.068891 Z4 E20456.473912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X119.768489 Y163.334341 Z4 E20456.989262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X119.342402 Y163.422376 Z4 E20457.324804 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X118.89735 Y163.51433 Z4 E20457.731304 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X117.854606 Y163.590842 Z4 E20458.883872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X117.062 Y163.649 Z4 E20459.962642 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X116.358628 Y163.59739 Z4 E20461.066569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X115.22665 Y163.51433 Z4 E20463.132649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X114.86922 Y163.44048 Z4 E20463.872893 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X114.355511 Y163.334341 Z4 E20465.001457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X113.523078 Y163.068891 Z4 E20467.050566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X113.430509 Y163.026754 Z4 E20467.302844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X112.735112 Y162.710212 Z4 E20469.289683 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X112.110493 Y162.321021 Z4 E20471.356423 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X111.997373 Y162.250537 Z4 E20471.746769 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X111.315624 Y161.682097 Z4 E20474.472018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X110.994129 Y161.326912 Z4 E20476.03363 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X110.695625 Y160.997125 Z4 E20477.540525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X110.143138 Y160.187852 Z4 E20481.053492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X110.108976 Y160.120746 Z4 E20481.334464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X109.663924 Y159.24651 Z4 E20485.138503 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X109.483769 Y158.759781 Z4 E20487.258925 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X109.263744 Y158.165331 Z4 E20489.894219 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X108.948359 Y156.936547 Z4 E20495.168496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X108.723531 Y155.55239 Z4 E20500.998572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X108.595021 Y154.005092 Z4 E20507.453639 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X108.568591 Y152.286885 Z4 E20514.59796 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X108.65 Y150.39 Z4 E20522.491549 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X108.426242 Y148.58957 Z4 E20530.034451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X108.369688 Y145.929313 Z4 E20541.097017 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X108.578914 Y142.543898 Z4 E20555.198788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X109.1525 Y138.568 Z4 E20571.899781 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X109.606733 Y136.400704 Z4 E20581.106123 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X110.189023 Y134.136289 Z4 E20590.826747 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X110.911692 Y131.791589 Z4 E20601.02739 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X111.787063 Y129.383438 Z4 E20611.680264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X112.827456 Y126.928669 Z4 E20622.76479 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X114.045195 Y124.444117 Z4 E20634.268337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X115.452603 Y121.946616 Z4 E20646.186935 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X117.062 Y119.453 Z4 E20658.525926 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X118.671397 Y121.946616 Z4 E20670.864916 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X120.078805 Y124.444117 Z4 E20682.783514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X121.296544 Y126.928669 Z4 E20694.287061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X122.336938 Y129.383438 Z4 E20705.371587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X123.212308 Y131.791589 Z4 E20716.024461 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X123.934977 Y134.136289 Z4 E20726.225104 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X124.517267 Y136.400704 Z4 E20735.945728 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X124.9715 Y138.568 Z4 E20745.15207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X125.545086 Y142.543898 Z4 E20761.853064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X125.754313 Y145.929313 Z4 E20775.954834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X125.697758 Y148.58957 Z4 E20787.0174 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X125.474 Y150.39 Z4 E20794.560302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X125.555409 Y152.286885 Z4 E20802.453892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X125.528979 Y154.005092 Z4 E20809.598212 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X125.400469 Y155.55239 Z4 E20816.053279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X125.175641 Y156.936547 Z4 E20821.883355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X124.860256 Y158.165331 Z4 E20827.157632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X124.844848 Y158.20696 Z4 E20827.342181 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X124.460076 Y159.24651 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
G1 X123.980862 Y160.187852 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
G1 X123.428375 Y160.997125 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
G1 X122.808376 Y161.682097 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
G1 X122.126627 Y162.250537 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
G1 X122.089446 Y162.273704 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0008
G0 X122.089446 Y162.273704 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0007 note=intra-page lift
G0 X126.804982 Y169.841731 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0007 note=intra-page XY
G0 X126.804982 Y169.841731 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0007 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0007
G1 X127.090762 Y170.445962 Z4 E20827.404096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X127.129515 Y170.527899 Z4.04532 E20827.424293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4 matz1=4.04532 note=collision lift
G1 X127.349559 Y171.14288 Z4.371901 E20827.653995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.04532 matz1=4.371901 note=collision lift
G1 X127.489779 Y171.534768 Z4.58001 E20827.877474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.371901 matz1=4.58001 note=collision lift
G1 X127.714638 Y172.432456 Z5.042721 E20828.589436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.58001 matz1=5.042721 note=collision lift
G1 X127.749617 Y172.572101 Z5.114701 E20828.726857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.042721 matz1=5.114701 note=collision lift
G1 X127.749631 Y172.572193 Z5.114747 E20828.726949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X127.906528 Y173.629907 Z5.649391 E20829.972444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.114747 matz1=5.649391 note=collision lift
G1 X127.912823 Y173.758054 Z5.713541 E20830.148505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.649391 matz1=5.713455 note=collision lift
G1 X127.940982 Y174.331234 Z6.000475 E20831.005801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.713455 matz1=6 note=collision lift
G1 X127.941029 Y174.332183 Z6 E20831.007314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X127.959 Y174.698 Z6 E20831.547963 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X127.934904 Y175.188482 Z6 E20832.331202 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X127.906528 Y175.766093 Z6 E20833.339279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X127.771288 Y176.677809 Z6 E20835.137525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X127.749617 Y176.823899 Z6 E20835.447557 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X127.489779 Y177.861232 Z6 E20837.872797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X127.394462 Y178.127624 Z6 E20838.567477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X127.129515 Y178.868101 Z6 E20840.615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X126.824433 Y179.513143 Z6 E20842.621056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X126.672296 Y179.83481 Z6 E20843.674165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X126.484001 Y180.148961 Z6 E20844.794786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X126.483513 Y180.149775 Z6.000475 E20844.798088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X126.126296 Y180.745755 Z5.65306 E20847.298262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=5.653055 note=collision lift
G1 X126.122524 Y180.752049 Z5.649391 E20847.325556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.653055 matz1=5.649391 note=collision lift
G1 X125.485551 Y181.610908 Z5.114747 E20851.502588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X125.485495 Y181.610984 Z5.114701 E20851.502972 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X125.307584 Y181.807278 Z4.982239 E20852.599096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.114701 matz1=4.982239 note=collision lift
G1 X124.767343 Y182.403343 Z4.58001 E20856.07659 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.982239 matz1=4.58001 note=collision lift
G1 X124.369317 Y182.764092 Z4.311419 E20858.523558 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.58001 matz1=4.311419 note=collision lift
G1 X123.974984 Y183.121495 Z4.04532 E20860.997346 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.311419 matz1=4.04532 note=collision lift
G1 X123.902181 Y183.175489 Z4 E20861.41866 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.04532 matz1=4 note=collision lift
G1 X123.116049 Y183.758524 Z4 E20865.487795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X122.19881 Y184.308296 Z4 E20869.933764 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X121.232101 Y184.765515 Z4 E20874.379733 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X120.225232 Y185.125779 Z4 E20878.825702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X119.187899 Y185.385617 Z4 E20883.271671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X118.130093 Y185.542528 Z4 E20887.71764 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X117.062 Y185.595 Z4 E20892.16361 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X115.993907 Y185.542528 Z4 E20896.609579 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X114.936101 Y185.385617 Z4 E20901.055548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X113.898768 Y185.125779 Z4 E20905.501517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X112.891899 Y184.765515 Z4 E20909.947486 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X112.542575 Y184.600298 Z4 E20911.554052 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X111.92519 Y184.308296 Z4.341478 E20914.728601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4 matz1=4.341478 note=collision lift
G1 X111.007951 Y183.758524 Z4.876169 E20919.699346 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X110.149016 Y183.121495 Z5.410859 E20924.67009 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X109.356657 Y182.403343 Z5.94555 E20929.640835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X108.638505 Y181.610984 Z6.48024 E20934.61158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.94555 matz1=6 note=collision lift
G1 X108.001476 Y180.752049 Z7.014931 E20939.582324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X107.451704 Y179.83481 Z7.549621 E20944.553069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X107.06658 Y179.020535 Z8 E20948.740013 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.994485 Y178.868101 Z8 E20949.441065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.634221 Y177.861232 Z8 E20953.887035 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.374383 Y176.823899 Z8 E20958.333004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.217472 Y175.766093 Z8 E20962.778973 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.165 Y174.698 Z8 E20967.224942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.217472 Y173.629907 Z8 E20971.670911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.292812 Y173.122006 Z8 E20973.805623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.292992 Y173.120795 Z8 E20973.810713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.374383 Y172.572101 Z7.737636 E20976.361834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.377449 Y172.55986 Z7.731326 E20976.420491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.418829 Y172.394661 Z7.652265 E20977.201105 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.420254 Y172.388973 Z7.655196 E20977.22836 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.634221 Y171.534768 Z7.220833 E20981.31061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X106.994485 Y170.527899 Z6.686142 E20986.281355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X107.451704 Y169.56119 Z6.151452 E20991.252099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X108.001476 Y168.643951 Z5.616761 E20996.222844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=5.616761 note=collision lift
G1 X108.638505 Y167.785016 Z5.082071 E21001.193588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X109.356657 Y166.992657 Z4.547381 E21006.164333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X110.149016 Y166.274505 Z4.01269 E21011.135078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X110.169402 Y166.259386 Z4 E21011.253051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.01269 matz1=4 note=collision lift
G1 X111.007951 Y165.637476 Z4 E21015.593501 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X111.92519 Y165.087704 Z4 E21020.039471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X112.891899 Y164.630485 Z4 E21024.48544 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X113.898768 Y164.270221 Z4 E21028.931409 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X114.936101 Y164.010383 Z4 E21033.377378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X115.993907 Y163.853472 Z4 E21037.823347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X117.062 Y163.801 Z4 E21042.269316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X118.130093 Y163.853472 Z4 E21046.715285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X119.187899 Y164.010383 Z4 E21051.161254 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X120.225232 Y164.270221 Z4 E21055.607224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X121.232101 Y164.630485 Z4 E21060.053193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X122.19881 Y165.087704 Z4 E21064.499162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X123.116049 Y165.637476 Z4 E21068.945131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X123.974984 Y166.274505 Z4 E21073.3911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X123.97886 Y166.278018 Z4 E21073.412848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X124.06073 Y166.352221 Z4.055247 E21073.926451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4 matz1=4.055247 note=collision lift
G1 X124.767343 Y166.992657 Z4.532075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.055247 matz1=4.532075 note=collision lift
G1 X125.485495 Y167.785016 Z5.066765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.532075 matz1=5.066765 note=collision lift
G1 X126.122524 Y168.643951 Z5.601456 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.066765 matz1=5.601456 note=collision lift
G1 X126.532314 Y169.327643 Z6.000004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.601456 matz1=6 note=collision lift
G1 X126.672296 Y169.56119 Z5.863862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=5.863862 note=collision lift
G1 X126.804982 Y169.841731 Z5.708693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.863862 matz1=5.708693 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0007
G0 X126.804982 Y169.841731 Z9.708693 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0006 note=intra-page lift
G0 X139.466093 Y163.853472 Z9.708693 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0006 note=intra-page XY
G0 X139.466093 Y163.853472 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0006 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0006
G1 X140.523899 Y164.010383 Z4 E21074.084932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X140.941613 Y164.115015 Z4 E21074.238264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X141.561232 Y164.270221 Z4 E21074.560375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X142.372126 Y164.560364 Z4 E21075.173706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X142.568101 Y164.630485 Z4 E21075.352781 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X143.53481 Y165.087704 Z4 E21076.462149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X143.725635 Y165.20208 Z4 E21076.732775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X144.452049 Y165.637476 Z4 E21077.888479 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X144.97662 Y166.026524 Z4 E21078.915471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X145.310984 Y166.274505 Z4 E21079.631772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X146.103343 Y166.992657 Z4 E21081.692027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X146.112969 Y167.003278 Z4 E21081.721795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X146.821495 Y167.785016 Z4 E21084.069244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X147.086553 Y168.142406 Z4 E21085.151746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X147.458524 Y168.643951 Z4 E21086.763424 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X147.908658 Y169.394954 Z4 E21089.205325 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X148.008296 Y169.56119 Z4 E21089.774565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X148.426762 Y170.445962 Z4 E21092.808289 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X148.465515 Y170.527899 Z4.04532 E21093.137567 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4 matz1=4.04532 note=collision lift
G1 X148.533648 Y170.718317 Z4.14644 E21093.882532 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.04532 matz1=4.14644 note=collision lift
G1 X148.825779 Y171.534768 Z4.58001 E21097.237334 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.14644 matz1=4.58001 note=collision lift
G1 X148.941073 Y171.995048 Z4.81726 E21099.183366 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.58001 matz1=4.81726 note=collision lift
G1 X149.085617 Y172.572101 Z5.114701 E21101.733305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.81726 matz1=5.114701 note=collision lift
G1 X149.085631 Y172.572193 Z5.114747 E21101.733716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X149.19519 Y173.310778 Z5.488081 E21105.107827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.114747 matz1=5.488081 note=collision lift
G1 X149.242528 Y173.629907 Z5.649391 E21106.607447 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.488081 matz1=5.649391 note=collision lift
G1 X149.276982 Y174.331234 Z6.000475 E21109.871313 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.649391 matz1=6 note=collision lift
G1 X149.277029 Y174.332183 Z6 E21109.875727 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X149.295 Y174.698 Z6 E21111.398454 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X149.242528 Y175.766093 Z6 E21115.844423 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X149.085617 Y176.823899 Z6 E21120.290392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X148.825779 Y177.861232 Z6 E21124.736361 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X148.465515 Y178.868101 Z6 E21129.18233 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X148.008296 Y179.83481 Z6 E21133.628299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X147.820001 Y180.148961 Z6 E21135.151026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X147.819513 Y180.149775 Z6.000475 E21135.15544 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X147.458524 Y180.752049 Z5.649391 E21138.419306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=5.649391 note=collision lift
G1 X146.821551 Y181.610908 Z5.114747 E21143.389615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X146.821495 Y181.610984 Z5.114701 E21143.39005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X146.103343 Y182.403343 Z4.58001 E21148.360795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X145.310984 Y183.121495 Z4.04532 E21153.331539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X145.238181 Y183.175489 Z4 E21153.752853 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.04532 matz1=4 note=collision lift
G1 X144.452049 Y183.758524 Z4 E21157.821988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X143.53481 Y184.308296 Z4 E21162.267957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X142.568101 Y184.765515 Z4 E21166.713926 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X141.561232 Y185.125779 Z4 E21171.159895 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X140.523899 Y185.385617 Z4 E21175.605864 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X139.466093 Y185.542528 Z4 E21180.051833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X138.398 Y185.595 Z4 E21184.497802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X137.329907 Y185.542528 Z4 E21188.943772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X136.272101 Y185.385617 Z4 E21193.389741 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X135.234768 Y185.125779 Z4 E21197.83571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X134.227899 Y184.765515 Z4 E21202.281679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X133.878575 Y184.600298 Z4 E21203.888245 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X133.26119 Y184.308296 Z4.341478 E21207.062794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4 matz1=4.341478 note=collision lift
G1 X132.343951 Y183.758524 Z4.876169 E21212.033539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X131.485016 Y183.121495 Z5.410859 E21217.004283 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X130.692657 Y182.403343 Z5.94555 E21221.975028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X129.974505 Y181.610984 Z6.48024 E21226.945773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.94555 matz1=6 note=collision lift
G1 X129.337476 Y180.752049 Z7.014931 E21231.916517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X128.787704 Y179.83481 Z7.549621 E21236.887262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X128.40258 Y179.020535 Z8 E21241.074206 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X128.330485 Y178.868101 Z8 E21241.775258 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.970221 Y177.861232 Z8 E21246.221227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.710383 Y176.823899 Z8 E21250.667197 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.553472 Y175.766093 Z8 E21255.113166 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.501 Y174.698 Z8 E21259.559135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.553472 Y173.629907 Z8 E21264.005104 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.628812 Y173.122006 Z8 E21266.139816 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.628992 Y173.120795 Z8 E21266.144905 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.710383 Y172.572101 Z7.737636 E21268.696027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.713449 Y172.55986 Z7.731326 E21268.754684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.754829 Y172.394661 Z7.652265 E21269.535298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.756254 Y172.388973 Z7.655196 E21269.562553 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X127.970221 Y171.534768 Z7.220833 E21273.644803 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X128.330485 Y170.527899 Z6.686142 E21278.615548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X128.787704 Y169.56119 Z6.151452 E21283.586292 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X129.337476 Y168.643951 Z5.616761 E21288.557037 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=5.616761 note=collision lift
G1 X129.974505 Y167.785016 Z5.082071 E21293.527781 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X130.692657 Y166.992657 Z4.547381 E21298.498526 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X131.485016 Y166.274505 Z4.01269 E21303.46927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X131.505402 Y166.259386 Z4 E21303.587244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.01269 matz1=4 note=collision lift
G1 X132.343951 Y165.637476 Z4 E21307.927694 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X133.26119 Y165.087704 Z4 E21312.373663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X134.227899 Y164.630485 Z4 E21316.819633 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X134.554524 Y164.513616 Z4 E21318.261894 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X135.234768 Y164.270221 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
G1 X136.272101 Y164.010383 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
G1 X137.329907 Y163.853472 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
G1 X138.398 Y163.801 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
G1 X139.466093 Y163.853472 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0006
G0 X139.466093 Y163.853472 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0005 note=intra-page lift
G0 X140.9912 Y150.325186 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0005 note=intra-page XY
G0 X140.9912 Y150.325186 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0005 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0005
G1 X140.865584 Y151.600588 Z4 E21318.489508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X140.802178 Y151.809609 Z4 E21318.573708 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X140.431962 Y153.030048 Z4 E21319.329349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X140.326065 Y153.228167 Z4 E21319.509149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X139.727798 Y154.347445 Z4 E21320.787658 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X139.58134 Y154.525905 Z4 E21321.068218 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X138.780154 Y155.502154 Z4 E21322.864433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X138.596886 Y155.652557 Z4 E21323.250914 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X137.625445 Y156.449798 Z4 E21325.559676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X137.410872 Y156.56449 Z4 E21326.057238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X136.308048 Y157.153962 Z4 E21328.873387 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X136.069272 Y157.226394 Z4 E21329.487189 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X134.878588 Y157.587584 Z4 E21332.805564 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X134.624081 Y157.612651 Z4 E21333.540768 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X133.392 Y157.734 Z4 E21337.356209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X133.131303 Y157.708324 Z4 E21338.217975 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X131.905412 Y157.587584 Z4 E21342.525321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X131.648783 Y157.509736 Z4 E21343.518809 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X130.475952 Y157.153962 Z4 E21348.312901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X130.233957 Y157.024613 Z4 E21349.44327 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X129.158555 Y156.449798 Z4 E21354.512887 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X128.003846 Y155.502154 Z4 E21360.723308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X127.056202 Y154.347445 Z4 E21366.933729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X126.352038 Y153.030048 Z4 E21373.144149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X125.918416 Y151.600588 Z4 E21379.35457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X125.772 Y150.114 Z4 E21385.56499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X125.918416 Y148.627412 Z4 E21391.775411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X126.352038 Y147.197952 Z4 E21397.985832 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X127.056202 Y145.880555 Z4 E21404.196252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X128.003846 Y144.725846 Z4 E21410.406673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X129.158555 Y143.778202 Z4 E21416.617094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X130.475952 Y143.074038 Z4 E21422.827514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X131.905412 Y142.640416 Z4 E21429.037935 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X133.392 Y142.494 Z4 E21435.248355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X134.878588 Y142.640416 Z4 E21441.458776 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X136.308048 Y143.074038 Z4 E21447.669197 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X137.625445 Y143.778202 Z4 E21453.879617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X138.780154 Y144.725846 Z4 E21460.090038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X139.533389 Y145.643667 Z4 E21465.026393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X139.727798 Y145.880555 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=end-early tail
G1 X140.431962 Y147.197952 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=end-early tail
G1 X140.865584 Y148.627412 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=end-early tail
G1 X141.012 Y150.114 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=end-early tail
G1 X140.9912 Y150.325186 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0005
G0 X140.9912 Y150.325186 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0004 note=intra-page lift
G0 X155.533631 Y151.75749 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0004 note=intra-page XY
G0 X155.533631 Y151.75749 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0004 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0004
G1 X154.780524 Y152.236459 Z4 E21465.136786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X154.23472 Y152.503175 Z4 E21465.338207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X153.989672 Y152.622922 Z4 E21465.461908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X153.159228 Y152.906886 Z4 E21465.999887 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X152.816193 Y152.974352 Z4 E21466.273648 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X152.287346 Y153.078361 Z4 E21466.762068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X151.372177 Y153.127355 Z4 E21467.777436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X151.327801 Y153.123497 Z4 E21467.832717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X150.411875 Y153.043875 Z4 E21469.096559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X149.845334 Y152.916794 Z4 E21470.015413 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X149.404593 Y152.81793 Z4 E21470.794857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X148.417719 Y152.464337 Z4 E21472.821737 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X148.348482 Y152.439529 Z4 E21472.975373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X147.241698 Y151.89868 Z4 E21475.771534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X147.075967 Y151.79671 Z4 E21476.251689 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X146.082391 Y151.185391 Z4 E21479.350329 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X145.814119 Y150.9874 Z4 E21480.305268 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X144.868715 Y150.28967 Z4 E21483.916146 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X144.621921 Y150.078198 Z4 E21484.982474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X143.598822 Y149.201525 Z4 E21489.715266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X143.489334 Y149.095121 Z4 E21490.283308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X142.413636 Y148.049715 Z4 E21496.20777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X142.270866 Y147.910966 Z4 E21497.035465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X140.883 Y146.408 Z4 E21505.540692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X139.352941 Y145.194027 Z4 E21513.660961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X137.285906 Y143.206781 Z4 E21525.582079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X134.85423 Y140.479145 Z4 E21540.774404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X132.23025 Y137.044 Z4 E21558.745985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X130.9 Y135.071388 Z4 E21568.637697 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X129.586301 Y132.93423 Z4 E21579.067389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X128.310693 Y130.636637 Z4 E21589.993127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X127.094719 Y128.182719 Z4 E21601.379191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X125.95992 Y125.576585 Z4 E21613.196853 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X124.92784 Y122.822348 Z4 E21625.425195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X124.020019 Y119.924116 Z4 E21638.051929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X123.258 Y116.886 Z4 E21651.074198 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X126.296116 Y117.648019 Z4 E21664.096468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X129.194348 Y118.55584 Z4 E21676.723201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X131.948585 Y119.58792 Z4 E21688.951543 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X134.554719 Y120.722719 Z4 E21700.769206 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X137.008637 Y121.938693 Z4 E21712.155269 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X139.30623 Y123.214301 Z4 E21723.081007 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X141.443388 Y124.528 Z4 E21733.5107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X143.416 Y125.85825 Z4 E21743.402411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X146.851145 Y128.48223 Z4 E21761.373992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X149.578781 Y130.913906 Z4 E21776.566317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X151.566027 Y132.980941 Z4 E21788.487435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X152.78 Y134.511 Z4 E21796.607704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X154.282966 Y135.898866 Z4 E21805.112931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X155.573525 Y137.226822 Z4 E21812.811649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X156.66167 Y138.496715 Z4 E21819.764385 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X157.557391 Y139.710391 Z4 E21826.03566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X158.27068 Y140.869698 Z4 E21831.694732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X158.811529 Y141.976482 Z4 E21836.816231 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X159.18993 Y143.032593 Z4 E21841.480357 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X159.415875 Y144.039875 Z4 E21845.772213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X159.499355 Y145.000177 Z4 E21849.779742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X159.450361 Y145.915346 Z4 E21853.59002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X159.278886 Y146.787228 Z4 E21857.284326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X158.994922 Y147.617672 Z4 E21860.933177 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X158.795042 Y148.026704 Z4 E21862.825917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X158.608459 Y148.408524 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X158.12949 Y149.161631 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X156.934 Y150.562 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X155.533631 Y151.75749 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0004
G0 X155.533631 Y151.75749 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0003 note=intra-page lift
G0 X165.524394 Y165.479447 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0003 note=intra-page XY
G0 X165.524394 Y165.479447 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0003 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0003
G1 X165.788049 Y165.637476 Z4 E21862.839012 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X166.646984 Y166.274505 Z4 E21863.088602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X166.738292 Y166.357262 Z4 E21863.137731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X167.439343 Y166.992657 Z4 E21863.655154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X167.811286 Y167.403034 Z4 E21864.073172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X168.157495 Y167.785016 Z4 E21864.538669 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X168.743943 Y168.57575 Z4 E21865.632241 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X168.794524 Y168.643951 Z4 E21865.739146 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X169.344296 Y169.56119 Z4 E21867.256585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X169.492105 Y169.873706 Z4 E21867.814938 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X169.762762 Y170.445962 Z4 E21868.923211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X169.801515 Y170.527899 Z4.04532 E21869.11094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4 matz1=4.04532 note=collision lift
G1 X170.032217 Y171.172667 Z4.387719 E21870.621261 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.04532 matz1=4.387719 note=collision lift
G1 X170.161779 Y171.534768 Z4.58001 E21871.540698 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.387719 matz1=4.58001 note=collision lift
G1 X170.394325 Y172.463145 Z5.05854 E21874.051213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.58001 matz1=5.05854 note=collision lift
G1 X170.421617 Y172.572101 Z5.114701 E21874.366658 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.05854 matz1=5.114701 note=collision lift
G1 X170.421631 Y172.572193 Z5.114747 E21874.366923 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.114701 matz1=5.114747 note=collision lift
G1 X170.578528 Y173.629907 Z5.649391 E21877.588821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.114747 matz1=5.649391 note=collision lift
G1 X170.586376 Y173.789653 Z5.72936 E21878.104792 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.649391 matz1=5.729251 note=collision lift
G1 X170.612982 Y174.331234 Z6.000475 E21879.920029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.729251 matz1=6 note=collision lift
G1 X170.613029 Y174.332183 Z6 E21879.923297 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X170.631 Y174.698 Z6 E21881.069446 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X170.605169 Y175.22381 Z6 E21882.781998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X170.578528 Y175.766093 Z6 E21884.628665 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X170.438098 Y176.712797 Z6 E21888.082832 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X170.421617 Y176.823899 Z6 E21888.504847 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X170.161779 Y177.861232 Z6 E21892.697991 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X170.054546 Y178.160927 Z6 E21894.007294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X169.801515 Y178.868101 Z6 E21897.129919 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X169.344296 Y179.83481 Z6 E21901.575889 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X169.156001 Y180.148961 Z6 E21903.098615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X169.155513 Y180.149775 Z6.000475 E21903.103029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X168.794524 Y180.752049 Z5.649391 E21906.366895 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=5.649391 note=collision lift
G1 X168.157551 Y181.610908 Z5.114747 E21911.337204 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.649391 matz1=5.114747 note=collision lift
G1 X168.157495 Y181.610984 Z5.114701 E21911.337639 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X167.439343 Y182.403343 Z4.58001 E21916.308384 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.114701 matz1=4.58001 note=collision lift
G1 X166.646984 Y183.121495 Z4.04532 E21921.279129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X166.574181 Y183.175489 Z4 E21921.700443 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.04532 matz1=4 note=collision lift
G1 X165.788049 Y183.758524 Z4 E21925.769577 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X164.87081 Y184.308296 Z4 E21930.215546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X163.904101 Y184.765515 Z4 E21934.661515 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X162.897232 Y185.125779 Z4 E21939.107484 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X161.859899 Y185.385617 Z4 E21943.553453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X160.802093 Y185.542528 Z4 E21947.999423 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X159.734 Y185.595 Z4 E21952.445392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X158.665907 Y185.542528 Z4 E21956.891361 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X157.608101 Y185.385617 Z4 E21961.33733 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X156.570768 Y185.125779 Z4 E21965.783299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X155.563899 Y184.765515 Z4 E21970.229268 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X155.214575 Y184.600298 Z4 E21971.835834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X154.59719 Y184.308296 Z4.341478 E21975.010383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4 matz1=4.341478 note=collision lift
G1 X153.679951 Y183.758524 Z4.876169 E21979.981128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X152.821016 Y183.121495 Z5.410859 E21984.951873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X152.028657 Y182.403343 Z5.94555 E21989.922617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X151.310505 Y181.610984 Z6.48024 E21994.893362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.94555 matz1=6 note=collision lift
G1 X150.673476 Y180.752049 Z7.014931 E21999.864106 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X150.123704 Y179.83481 Z7.549621 E22004.834851 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.73858 Y179.020535 Z8 E22009.021795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.666485 Y178.868101 Z8 E22009.722848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.306221 Y177.861232 Z8 E22014.168817 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.046383 Y176.823899 Z8 E22018.614786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X148.889472 Y175.766093 Z8 E22023.060755 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X148.837 Y174.698 Z8 E22027.506724 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X148.889472 Y173.629907 Z8 E22031.952693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X148.964812 Y173.122006 Z8 E22034.087405 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X148.964992 Y173.120795 Z8 E22034.092495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.046383 Y172.572101 Z7.737636 E22036.643616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.049449 Y172.55986 Z7.731326 E22036.702273 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.090829 Y172.394661 Z7.652265 E22037.482888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.092254 Y172.388973 Z7.655196 E22037.510142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.306221 Y171.534768 Z7.220833 E22041.592392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X149.666485 Y170.527899 Z6.686142 E22046.563137 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X150.123704 Y169.56119 Z6.151452 E22051.533881 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X150.673476 Y168.643951 Z5.616761 E22056.504626 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=5.616761 note=collision lift
G1 X151.310505 Y167.785016 Z5.082071 E22061.475371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X152.028657 Y166.992657 Z4.547381 E22066.446115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X152.821016 Y166.274505 Z4.01269 E22071.41686 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X152.841402 Y166.259386 Z4 E22071.534833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.01269 matz1=4 note=collision lift
G1 X153.679951 Y165.637476 Z4 E22075.875284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X154.59719 Y165.087704 Z4 E22080.321253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X155.563899 Y164.630485 Z4 E22084.767222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X156.570768 Y164.270221 Z4 E22089.213191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X157.608101 Y164.010383 Z4 E22093.65916 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X158.665907 Y163.853472 Z4 E22098.105129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X159.734 Y163.801 Z4 E22102.551098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X160.802093 Y163.853472 Z4 E22106.997067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X160.841182 Y163.85927 Z4 E22107.16136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X161.859899 Y164.010383 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
G1 X162.897232 Y164.270221 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
G1 X163.904101 Y164.630485 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
G1 X164.87081 Y165.087704 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
G1 X165.524394 Y165.479447 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0003
G0 X165.524394 Y165.479447 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0002 note=intra-page lift
G0 X169.440962 Y158.945048 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0002 note=intra-page XY
G0 X169.440962 Y158.945048 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0002
G1 X168.736798 Y160.262445 Z4 E22107.470594 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X168.732853 Y160.267252 Z4 E22107.473174 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X167.789154 Y161.417154 Z4 E22108.398295 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X167.779539 Y161.425044 Z4 E22108.408615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X166.634445 Y162.364798 Z4 E22109.944463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X166.617992 Y162.373593 Z4 E22109.967684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X165.317048 Y163.068962 Z4 E22112.109099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X165.293244 Y163.076183 Z4 E22112.150381 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X163.887588 Y163.502584 Z4 E22114.892202 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X163.856644 Y163.505632 Z4 E22114.956705 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X162.401 Y163.649 Z4 E22118.293772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X162.363867 Y163.645343 Z4 E22118.386656 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X160.914412 Y163.502584 Z4 E22122.31381 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X160.872755 Y163.489947 Z4 E22122.440235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X159.484952 Y163.068962 Z4 E22126.952314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X159.441076 Y163.04551 Z4 E22127.117441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X158.167555 Y162.364798 Z4 E22132.209287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X158.12429 Y162.329292 Z4 E22132.418275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X157.012846 Y161.417154 Z4 E22138.084726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X156.973395 Y161.369082 Z4 E22138.342737 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X156.065202 Y160.262445 Z4 E22144.294611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X155.361038 Y158.945048 Z4 E22150.505031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X154.927416 Y157.515588 Z4 E22156.715452 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X154.781 Y156.029 Z4 E22162.925873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X154.927416 Y154.542412 Z4 E22169.136293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X155.361038 Y153.112952 Z4 E22175.346714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X156.065202 Y151.795555 Z4 E22181.557135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X157.012846 Y150.640846 Z4 E22187.767555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X158.167555 Y149.693202 Z4 E22193.977976 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X159.484952 Y148.989038 Z4 E22200.188396 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X160.914412 Y148.555416 Z4 E22206.398817 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X162.401 Y148.409 Z4 E22212.609238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X163.887588 Y148.555416 Z4 E22218.819658 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X165.317048 Y148.989038 Z4 E22225.030079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X166.634445 Y149.693202 Z4 E22231.2405 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X167.789154 Y150.640846 Z4 E22237.45092 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X168.736798 Y151.795555 Z4 E22243.661341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X169.440962 Y153.112952 Z4 E22249.871762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X169.724026 Y154.046089 Z4 E22253.92586 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X169.874584 Y154.542412 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X170.021 Y156.029 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X169.874584 Y157.515588 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X169.440962 Y158.945048 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0002
G0 X169.440962 Y158.945048 Z8.638497 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0001 note=intra-page lift
G0 X184.119993 Y163.818144 Z8.638497 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0001 note=intra-page XY
G0 X184.119993 Y163.818144 Z4.638497 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0001
G1 X183.552103 Y163.960393 Z4.930949 E22253.98521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.638497 matz1=4.930949 note=collision lift
G1 X183.552068 Y163.960401 Z4.930931 E22253.985217 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.930949 matz1=4.930931 note=collision lift
G1 X183.196167 Y164.04955 Z5.114378 E22254.082944 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.930931 matz1=5.114378 note=collision lift
G1 X183.195899 Y164.049617 Z5.114701 E22254.08307 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.114378 matz1=5.114701 note=collision lift
G1 X182.811108 Y164.106696 Z5.3092 E22254.237673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.114701 matz1=5.3092 note=collision lift
G1 X182.501327 Y164.152647 Z5.465784 E22254.400232 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.3092 matz1=5.465784 note=collision lift
G1 X182.501148 Y164.152674 Z5.465694 E22254.400336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.465784 matz1=5.465694 note=collision lift
G1 X182.138672 Y164.206442 Z5.648914 E22254.63371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.465694 matz1=5.648914 note=collision lift
G1 X182.138093 Y164.206528 Z5.649391 E22254.634184 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.648914 matz1=5.649391 note=collision lift
G1 X181.477716 Y164.23897 Z5.979975 E22255.173115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.649391 matz1=5.979528 note=collision lift
G1 X181.436766 Y164.240982 Z6.000475 E22255.211521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.979528 matz1=6 note=collision lift
G1 X181.435817 Y164.241029 Z6 E22255.212417 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y164.259 Z6 E22255.540314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y164.206528 Z6 E22256.710448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X179.984636 Y164.203966 Z6 E22256.732184 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y164.049617 Z6 E22258.197545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X178.50945 Y163.940743 Z6 E22258.91488 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y163.789779 Z6 E22260.001604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X177.079434 Y163.493754 Z6 E22261.721204 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y163.429515 Z6 E22262.122625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y162.972296 Z6 E22264.560609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X175.727389 Y162.848944 Z6 E22265.151155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X175.619039 Y162.784001 Z6 E22265.468478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X175.618225 Y162.783513 Z6.000475 E22265.471164 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X175.015951 Y162.422524 Z5.649391 E22267.542611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=5.649391 note=collision lift
G1 X174.593838 Y162.109464 Z5.386624 E22269.204734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.649391 matz1=5.386624 note=collision lift
G1 X174.157092 Y161.785551 Z5.114747 E22271.025202 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.386624 matz1=5.114747 note=collision lift
G1 X174.157016 Y161.785495 Z5.114701 E22271.025525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.114747 matz1=5.114701 note=collision lift
G1 X173.56589 Y161.249729 Z4.715804 E22273.881941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.114701 matz1=4.715804 note=collision lift
G1 X173.364657 Y161.067343 Z4.58001 E22274.904641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.715804 matz1=4.58001 note=collision lift
G1 X172.646505 Y160.274984 Z4.04532 E22279.179961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.58001 matz1=4.04532 note=collision lift
G1 X172.646104 Y160.274443 Z4.044983 E22279.182775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.04532 matz1=4.044983 note=collision lift
G1 X172.592511 Y160.202181 Z4 E22279.560545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.044983 matz1=4 note=collision lift
G1 X172.009476 Y159.416049 Z4 E22283.382807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X171.793207 Y159.055226 Z4 E22285.107236 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X171.459704 Y158.49881 Z4 E22287.804252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X171.002485 Y157.532101 Z4 E22292.250221 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X170.642221 Y156.525232 Z4 E22296.69619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X170.382383 Y155.487899 Z4 E22301.142159 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X170.225472 Y154.430093 Z4 E22305.588128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X170.173 Y153.362 Z4 E22310.034097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X170.225472 Y152.293907 Z4 E22314.480066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X170.382383 Y151.236101 Z4 E22318.926035 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X170.642221 Y150.198768 Z4 E22323.372005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X171.002485 Y149.191899 Z4 E22327.817974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X171.167702 Y148.842575 Z4 E22329.424539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X171.459704 Y148.22519 Z4.341478 E22332.599089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4 matz1=4.341478 note=collision lift
G1 X172.009476 Y147.307951 Z4.876169 E22337.569833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.341478 matz1=4.876169 note=collision lift
G1 X172.646505 Y146.449016 Z5.410859 E22342.540578 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X173.364657 Y145.656657 Z5.94555 E22347.511323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X174.157016 Y144.938505 Z6.48024 E22352.482067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.94555 matz1=6 note=collision lift
G1 X175.015951 Y144.301476 Z7.014931 E22357.452812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y143.751704 Z7.549621 E22362.423556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X176.747465 Y143.36658 Z8 E22366.610501 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y143.294485 Z8 E22367.311553 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y142.934221 Z8 E22371.757522 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y142.674383 Z8 E22376.203491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y142.517472 Z8 E22380.64946 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y142.465 Z8 E22385.095429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y142.517472 Z8 E22389.541399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X182.645994 Y142.592812 Z8 E22391.676111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X182.647205 Y142.592992 Z8 E22391.6812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y142.674383 Z7.737636 E22394.232321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X183.20814 Y142.677449 Z7.731326 E22394.290978 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X183.373339 Y142.718829 Z7.652265 E22395.071593 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X183.379027 Y142.720254 Z7.655196 E22395.098848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y142.934221 Z7.220833 E22399.181098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y143.294485 Z6.686142 E22404.151842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y143.751704 Z6.151452 E22409.122587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X187.124049 Y144.301476 Z5.616761 E22414.093331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=5.616761 note=collision lift
G1 X187.982984 Y144.938505 Z5.082071 E22419.064076 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.616761 matz1=5.082071 note=collision lift
G1 X188.775343 Y145.656657 Z4.547381 E22424.034821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.082071 matz1=4.547381 note=collision lift
G1 X189.493495 Y146.449016 Z4.01269 E22429.005565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.547381 matz1=4.01269 note=collision lift
G1 X189.508614 Y146.469402 Z4 E22429.123538 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.01269 matz1=4 note=collision lift
G1 X190.130524 Y147.307951 Z4 E22433.463989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X190.680296 Y148.22519 Z4 E22437.909958 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.137515 Y149.191899 Z4 E22442.355927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.497779 Y150.198768 Z4 E22446.801896 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.757617 Y151.236101 Z4 E22451.247865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.914528 Y152.293907 Z4 E22455.693835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.967 Y153.362 Z4 E22460.139804 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.914528 Y154.430093 Z4 E22464.585773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.757617 Y155.487899 Z4 E22469.031742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.497779 Y156.525232 Z4 E22473.477711 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X191.137515 Y157.532101 Z4 E22477.92368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X190.680296 Y158.49881 Z4 E22482.369649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X190.130524 Y159.416049 Z4 E22486.815618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X189.493495 Y160.274984 Z4 E22491.261588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X189.472647 Y160.297985 Z4 E22491.390652 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X188.775343 Y161.067343 Z4.519169 E22496.217098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4 matz1=4.519169 note=collision lift
G1 X188.133396 Y161.649169 Z4.952359 E22500.244251 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.519169 matz1=4.952359 note=collision lift
G1 X187.982984 Y161.785495 Z5.053859 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.952359 matz1=5.053859 note=collision lift
G1 X187.124049 Y162.422524 Z5.58855 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.053859 matz1=5.58855 note=collision lift
G1 X186.20681 Y162.972296 Z6.12324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.58855 matz1=6 note=collision lift
G1 X185.322038 Y163.390762 Z6.612611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X185.29863 Y163.401833 Z6.638505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y163.429515 Z6.638505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X184.578975 Y163.66607 Z6.638503 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X184.578805 Y163.666131 Z6.638323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y163.789779 Z6.638321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X184.233218 Y163.789782 Z6.638306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X184.119993 Y163.818144 Z6.638306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0001
G0 X184.119993 Y163.818144 Z10.638306 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0000 note=intra-page lift
G0 X188.775343 Y182.403343 Z10.638306 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0000 note=intra-page XY
G0 X188.775343 Y182.403343 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0000 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0000
G1 X187.982984 Y183.121495 Z4 E22500.402733 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X187.637107 Y183.378014 Z4 E22500.556065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X187.124049 Y183.758524 Z4 E22500.878176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X186.38534 Y184.201289 Z4 E22501.491507 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X186.20681 Y184.308296 Z4 E22501.670582 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X185.240101 Y184.765515 Z4 E22502.77995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X185.03063 Y184.840465 Z4 E22503.050575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X184.233232 Y185.125779 Z4 E22504.20628 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X183.599709 Y185.284468 Z4 E22505.233272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X183.195899 Y185.385617 Z4 E22505.949573 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X182.138093 Y185.542528 Z4 E22508.009828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X182.123776 Y185.543231 Z4 E22508.039596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X181.07 Y185.595 Z4 E22510.387045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X180.625583 Y185.573167 Z4 E22511.469547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X180.001907 Y185.542528 Z4 E22513.081224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X179.135812 Y185.414055 Z4 E22515.523126 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X178.944101 Y185.385617 Z4 E22516.092366 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X177.906768 Y185.125779 Z4 E22519.42047 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X177.683801 Y185.046 Z4 E22520.200332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X176.899899 Y184.765515 Z4 E22523.065537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X176.550575 Y184.600298 Z4 E22524.460655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X176.323368 Y184.492837 Z4.125669 E22525.501167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4 matz1=4.125669 note=collision lift
G1 X175.93319 Y184.308296 Z4.341478 E22527.339078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4.125669 matz1=4.341478 note=collision lift
G1 X175.152637 Y183.840451 Z4.79649 E22531.425628 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4.341478 matz1=4.79649 note=collision lift
G1 X175.015951 Y183.758524 Z4.876169 E22532.166364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4.79649 matz1=4.876169 note=collision lift
G1 X174.157016 Y183.121495 Z5.410859 E22537.137109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4.876169 matz1=5.410859 note=collision lift
G1 X173.364657 Y182.403343 Z5.94555 E22542.107853 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X172.646505 Y181.610984 Z6.48024 E22547.078598 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.94555 matz1=6 note=collision lift
G1 X172.009476 Y180.752049 Z7.014931 E22552.049342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X171.459704 Y179.83481 Z7.549621 E22557.020087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X171.07458 Y179.020535 Z8 E22561.207032 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X171.002485 Y178.868101 Z8 E22561.908084 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.642221 Y177.861232 Z8 E22566.354053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.382383 Y176.823899 Z8 E22570.800022 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.225472 Y175.766093 Z8 E22575.245991 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.173 Y174.698 Z8 E22579.69196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.225472 Y173.629907 Z8 E22584.137929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.300812 Y173.122006 Z8 E22586.272641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.300992 Y173.120795 Z8 E22586.277731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.382383 Y172.572101 Z7.737636 E22588.828852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.385449 Y172.55986 Z7.731326 E22588.887509 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.426829 Y172.394661 Z7.652265 E22589.668124 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.428254 Y172.388973 Z7.655196 E22589.695378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X170.642221 Y171.534768 Z7.220833 E22593.777628 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X171.002485 Y170.527899 Z6.686142 E22598.748373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X171.459704 Y169.56119 Z6.151452 E22603.719117 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X172.009476 Y168.643951 Z5.616761 E22608.689862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=5.616761 note=collision lift
G1 X172.450646 Y168.049102 Z5.246465 E22612.132318 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.616761 matz1=5.246465 note=collision lift
G1 X172.646505 Y167.785016 Z5.410859 E22613.660607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.246465 matz1=5.410859 note=collision lift
G1 X173.364657 Y166.992657 Z5.94555 E22618.631351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.410859 matz1=5.94555 note=collision lift
G1 X174.157016 Y166.274505 Z6.48024 E22623.602096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.94555 matz1=6 note=collision lift
G1 X175.015951 Y165.637476 Z7.014931 E22628.57284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X175.93319 Y165.087704 Z7.549621 E22633.543585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X176.747465 Y164.70258 Z8 E22637.730529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X176.899899 Y164.630485 Z8 E22638.431582 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X177.906768 Y164.270221 Z8 E22642.877551 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X178.944101 Y164.010383 Z8 E22647.32352 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X180.001907 Y163.853472 Z8 E22651.769489 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X181.07 Y163.801 Z8 E22656.215458 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X182.138093 Y163.853472 Z8 E22660.661427 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X182.645994 Y163.928812 Z8 E22662.796139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X182.647205 Y163.928992 Z8 E22662.801229 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X182.766524 Y163.946691 Z7.943425 E22663.355147 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X182.878449 Y163.963293 Z8 E22663.881094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X183.195899 Y164.010383 Z8 E22665.215341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X184.233232 Y164.270221 Z8 E22669.66131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X185.240101 Y164.630485 Z8 E22674.107279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X185.392535 Y164.70258 Z8 E22674.808331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X186.20681 Y165.087704 Z7.549621 E22678.995276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X187.124049 Y165.637476 Z7.014931 E22683.96602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X187.982984 Y166.274505 Z6.48024 E22688.936765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X188.775343 Y166.992657 Z5.94555 E22693.90751 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=5.94555 note=collision lift
G1 X189.493495 Y167.785016 Z5.410859 E22698.878254 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.94555 matz1=5.410859 note=collision lift
G1 X190.130524 Y168.643951 Z4.876169 E22703.848999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.410859 matz1=4.876169 note=collision lift
G1 X190.680296 Y169.56119 Z4.341478 E22708.819743 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4.876169 matz1=4.341478 note=collision lift
G1 X190.972298 Y170.178575 Z4 E22711.994293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4.341478 matz1=4 note=collision lift
G1 X191.137515 Y170.527899 Z4 E22713.600859 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.497779 Y171.534768 Z4 E22718.046828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.757617 Y172.572101 Z4 E22722.492797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.914528 Y173.629907 Z4 E22726.938766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.967 Y174.698 Z4 E22731.384735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.914528 Y175.766093 Z4 E22735.830704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.757617 Y176.823899 Z4 E22740.276673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.497779 Y177.861232 Z4 E22744.722642 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.38091 Y178.187858 Z4 E22746.164904 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X191.137515 Y178.868101 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X190.680296 Y179.83481 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X190.130524 Y180.752049 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X189.493495 Y181.610984 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X188.775343 Y182.403343 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0000
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
