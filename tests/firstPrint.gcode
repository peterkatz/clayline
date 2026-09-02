; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=alhambra-lattice-job
; prepared_trace_sha256=4b407afa4523281ba9c1fda7680bc4080750ae67f04336d77516c86da0a94d8c
; body_sha256=45a0cf7e8ac4b61f6b7c18a07e753171759d496aa11458f1d5df3af186830c7c
; profile_name=potterbot-xl
; profile_version=1.1.0
; profile_verified=true
; profile_flavor=marlin
; extrusion_mode=absolute
; bead_width_mm=5
; layer_height_mm=2
; flow_multiplier=1
; wet_density_g_cm3=1.8
; prime_mm=15
; end_early_mm=5
; first_layer_z_mm=20
; speed_default_mm_s=40
; speed_first_layer_mm_s=30
; speed_travel_mm_s=120
; virtual_filament_diameter_mm=1.75
; work_bounds=17,398,12,393,0,710
; machine_envelope=0,490,0,490,0,710
; stats.motion_count=2164
; stats.print_motion_count=2073
; stats.travel_motion_count=91
; stats.stroke_count=31
; stats.page_count=2
; stats.print_path_mm=4410.407068
; stats.deposited_path_mm=4255.407068
; stats.travel_path_mm=1289.127829
; stats.total_motion_path_mm=5699.534898
; stats.motion_time_seconds=121.002909
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=121.002909
; stats.body_volume_mm3=40229.070682
; stats.wet_weight_g=72.412327
; stats.body_e=16725.304046
; stats.pressure_e_excluded=0
; stats.warning_count=212
; nominal_label=nominal — drape mode: physical bead placement depends on fall
; stats.warning_count.over_void=145
; stats.warning_count.tight_radius=13
; stats.warning_count.under_spaced=54
; parameter.alternate=true
; parameter.first_layer_height=2.0
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.layers=1
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_mode=stack
; parameter.page_pause_seconds=disabled
; parameter.page_travel_clearance=50.0
; parameter.provisional_flow_multiplier=1.0
; parameter.stack_job_page_count=2
; parameter.stack_page_0_path_start_z_mm=20.0
; parameter.stack_page_0_z_max_mm=20.0
; parameter.stack_page_0_z_min_mm=20.0
; parameter.stack_page_1_path_start_z_mm=22.0
; parameter.stack_page_1_prior_top_mm=2.0
; parameter.stack_page_1_z_max_mm=22.0
; parameter.stack_page_1_z_min_mm=22.0
; parameter.stack_page_material_height_mm=2.0
; parameter.stack_total_height_mm=4.0
; parameter.standoff_z=20.0
; parameter.z_mode=drape
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
G1 E3000 F40000 ; Prine Extruder
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-01-alhambra-lattice page_name=alhambra-lattice z_mode=drape
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X274.718461 Y269.718461 Z20 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start
G1 X275.725799 Y268.607034 Z20 E0.311814 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X276.225019 Y268.05623 Z20 E0.697455 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X276.675741 Y267.448503 Z20 E1.247255 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X277.561395 Y266.254336 Z20 E2.78982 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X277.568208 Y266.242969 Z20 E2.806324 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X278.339362 Y264.956376 Z20 E4.98902 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X278.71472 Y264.330129 Z20 E6.277095 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X279.043885 Y263.634168 Z20 E7.795344 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X279.673886 Y262.302143 Z20 E11.159279 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X279.682815 Y262.277189 Z20 E11.225296 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X280.18815 Y260.864873 Z20 E15.278875 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X280.429656 Y260.189908 Z20 E17.436374 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X280.619941 Y259.430247 Z20 E19.956081 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X280.974752 Y258.013765 Z20 E25.108378 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X280.980585 Y257.974439 Z20 E25.256915 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X281.200681 Y256.490675 Z20 E31.181377 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X281.303923 Y255.794672 Z20 E34.106682 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.414 Y253.554 Z20 E43.433548 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X281.303923 Y251.313328 Z20 E52.760413 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.974752 Y249.094235 Z20 E62.087279 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.429656 Y246.918092 Z20 E71.414145 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.673886 Y244.805857 Z20 E80.74101 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.71472 Y242.777871 Z20 E90.067876 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.561395 Y240.853664 Z20 E99.394741 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X276.225019 Y239.05177 Z20 E108.721607 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.718461 Y237.389539 Z20 E118.048472 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.05623 Y235.882981 Z20 E127.375338 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X271.254336 Y234.546605 Z20 E136.702204 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.330129 Y233.39328 Z20 E146.029069 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.302143 Y232.434114 Z20 E155.355935 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.189908 Y231.678344 Z20 E164.6828 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X263.013765 Y231.133248 Z20 E174.009666 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.794672 Y230.804077 Z20 E183.336531 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.554 Y230.694 Z20 E192.663397 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X256.313328 Y230.804077 Z20 E201.990263 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X254.094235 Y231.133248 Z20 E211.317128 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.918092 Y231.678344 Z20 E220.643994 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.805857 Y232.434114 Z20 E229.970859 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.777871 Y233.39328 Z20 E239.297725 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.853664 Y234.546605 Z20 E248.62459 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.05177 Y235.882981 Z20 E257.951456 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.389539 Y237.389539 Z20 E267.278322 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.882981 Y239.05177 Z20 E276.605187 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.546605 Y240.853664 Z20 E285.932053 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.39328 Y242.777871 Z20 E295.258918 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.434114 Y244.805857 Z20 E304.585784 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.678344 Y246.918092 Z20 E313.912649 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.133248 Y249.094235 Z20 E323.239515 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.804077 Y251.313328 Z20 E332.566381 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.694 Y253.554 Z20 E341.893246 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.804077 Y255.794672 Z20 E351.220112 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.133248 Y258.013765 Z20 E360.546977 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.678344 Y260.189908 Z20 E369.873843 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.434114 Y262.302143 Z20 E379.200708 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.39328 Y264.330129 Z20 E388.527574 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.546605 Y266.254336 Z20 E397.854439 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.882981 Y268.05623 Z20 E407.181305 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.389539 Y269.718461 Z20 E416.508171 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.05177 Y271.225019 Z20 E425.835036 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.853664 Y272.561395 Z20 E435.161902 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.777871 Y273.71472 Z20 E444.488767 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.805857 Y274.673886 Z20 E453.815633 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.918092 Y275.429656 Z20 E463.142498 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X254.094235 Y275.974752 Z20 E472.469364 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X256.313328 Y276.303923 Z20 E481.79623 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.554 Y276.414 Z20 E491.123095 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.794672 Y276.303923 Z20 E500.449961 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X263.013765 Y275.974752 Z20 E509.776826 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.189908 Y275.429656 Z20 E519.103692 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.302143 Y274.673886 Z20 E528.430557 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.330129 Y273.71472 Z20 E537.757423 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.814105 Y272.82526 Z20 E544.950435 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X271.254336 Y272.561395 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X273.05623 Y271.225019 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X274.718461 Y269.718461 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G0 X274.718461 Y269.718461 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0001 note=intra-page lift
G0 X265.189908 Y241.393656 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0001 note=intra-page XY
G0 X265.189908 Y241.393656 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X266.602224 Y240.888321 Z20 E545.262249 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X267.302143 Y240.637886 Z20 E545.64789 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X267.986125 Y240.314387 Z20 E546.19769 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X269.330129 Y239.67872 Z20 E547.740255 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X269.341496 Y239.671907 Z20 E547.756759 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X270.628089 Y238.900753 Z20 E549.939456 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X271.254336 Y238.525395 Z20 E551.22753 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X271.872707 Y238.06678 Z20 E552.745779 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X273.05623 Y237.189019 Z20 E556.109714 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X273.075868 Y237.17122 Z20 E556.175731 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X274.187295 Y236.163882 Z20 E560.22931 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X274.718461 Y235.682461 Z20 E562.386809 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X275.244379 Y235.1022 Z20 E564.906516 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X276.225019 Y234.02023 Z20 E570.058813 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X276.248701 Y233.988298 Z20 E570.20735 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X277.14225 Y232.783487 Z20 E576.131812 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X277.561395 Y232.218336 Z20 E579.057118 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X278.71472 Y230.294129 Z20 E588.383983 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X279.673886 Y228.266143 Z20 E597.710849 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.429656 Y226.153908 Z20 E607.037714 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.974752 Y223.977765 Z20 E616.36458 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.303923 Y221.758672 Z20 E625.691445 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.414 Y219.518 Z20 E635.018311 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.303923 Y217.277328 Z20 E644.345177 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.974752 Y215.058235 Z20 E653.672042 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.429656 Y212.882092 Z20 E662.998908 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X279.673886 Y210.769857 Z20 E672.325773 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X278.71472 Y208.741871 Z20 E681.652639 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X277.561395 Y206.817664 Z20 E690.979504 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X276.225019 Y205.01577 Z20 E700.30637 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.718461 Y203.353539 Z20 E709.633236 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X273.05623 Y201.846981 Z20 E718.960101 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X271.254336 Y200.510605 Z20 E728.286967 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X269.330129 Y199.35728 Z20 E737.613832 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X267.302143 Y198.398114 Z20 E746.940698 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X265.189908 Y197.642344 Z20 E756.267563 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X263.013765 Y197.097248 Z20 E765.594429 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.794672 Y196.768077 Z20 E774.921295 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X258.554 Y196.658 Z20 E784.24816 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X256.313328 Y196.768077 Z20 E793.575026 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X254.094235 Y197.097248 Z20 E802.901891 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X251.918092 Y197.642344 Z20 E812.228757 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X249.805857 Y198.398114 Z20 E821.555622 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X247.777871 Y199.35728 Z20 E830.882488 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X245.853664 Y200.510605 Z20 E840.209354 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.05177 Y201.846981 Z20 E849.536219 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X242.389539 Y203.353539 Z20 E858.863085 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.882981 Y205.01577 Z20 E868.18995 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.546605 Y206.817664 Z20 E877.516816 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.39328 Y208.741871 Z20 E886.843681 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.434114 Y210.769857 Z20 E896.170547 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X236.678344 Y212.882092 Z20 E905.497412 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X236.133248 Y215.058235 Z20 E914.824278 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X235.804077 Y217.277328 Z20 E924.151144 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X235.694 Y219.518 Z20 E933.478009 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X235.804077 Y221.758672 Z20 E942.804875 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X236.133248 Y223.977765 Z20 E952.13174 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X236.678344 Y226.153908 Z20 E961.458606 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.434114 Y228.266143 Z20 E970.785471 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.39328 Y230.294129 Z20 E980.112337 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.546605 Y232.218336 Z20 E989.439203 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.882981 Y234.02023 Z20 E998.766068 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X242.389539 Y235.682461 Z20 E1008.092934 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.05177 Y237.189019 Z20 E1017.419799 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X245.853664 Y238.525395 Z20 E1026.746665 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X247.777871 Y239.67872 Z20 E1036.07353 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X249.805857 Y240.637886 Z20 E1045.400396 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X251.918092 Y241.393656 Z20 E1054.727262 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X254.094235 Y241.938752 Z20 E1064.054127 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X256.313328 Y242.267923 Z20 E1073.380993 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X258.554 Y242.378 Z20 E1082.707858 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.282038 Y242.293107 Z20 E1089.900871 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.794672 Y242.267923 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
G1 X263.013765 Y241.938752 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
G1 X265.189908 Y241.393656 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
G0 X265.189908 Y241.393656 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0002 note=intra-page lift
G0 X246.393656 Y246.918092 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0002 note=intra-page XY
G0 X246.393656 Y246.918092 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0002
G1 X245.888321 Y245.505776 Z20 E1090.212684 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X245.637886 Y244.805857 Z20 E1090.598325 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X245.314387 Y244.121875 Z20 E1091.148126 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X244.67872 Y242.777871 Z20 E1092.69069 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X244.671907 Y242.766504 Z20 E1092.707194 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X243.900753 Y241.479911 Z20 E1094.889891 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X243.525395 Y240.853664 Z20 E1096.177965 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X243.06678 Y240.235293 Z20 E1097.696215 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X242.189019 Y239.05177 Z20 E1101.06015 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X242.17122 Y239.032132 Z20 E1101.126166 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X241.163882 Y237.920705 Z20 E1105.179745 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X240.682461 Y237.389539 Z20 E1107.337244 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X240.1022 Y236.863621 Z20 E1109.856952 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X239.02023 Y235.882981 Z20 E1115.009249 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X238.988298 Y235.859299 Z20 E1115.157786 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X237.783487 Y234.96575 Z20 E1121.082247 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X237.218336 Y234.546605 Z20 E1124.007553 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X235.294129 Y233.39328 Z20 E1133.334418 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X233.266143 Y232.434114 Z20 E1142.661284 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X231.153908 Y231.678344 Z20 E1151.98815 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X228.977765 Y231.133248 Z20 E1161.315015 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X226.758672 Y230.804077 Z20 E1170.641881 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X224.518 Y230.694 Z20 E1179.968746 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X222.277328 Y230.804077 Z20 E1189.295612 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X220.058235 Y231.133248 Z20 E1198.622477 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X217.882092 Y231.678344 Z20 E1207.949343 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X215.769857 Y232.434114 Z20 E1217.276209 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X213.741871 Y233.39328 Z20 E1226.603074 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X211.817664 Y234.546605 Z20 E1235.92994 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X210.01577 Y235.882981 Z20 E1245.256805 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X208.353539 Y237.389539 Z20 E1254.583671 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X206.846981 Y239.05177 Z20 E1263.910536 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X205.510605 Y240.853664 Z20 E1273.237402 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X204.35728 Y242.777871 Z20 E1282.564268 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X203.398114 Y244.805857 Z20 E1291.891133 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X202.642344 Y246.918092 Z20 E1301.217999 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X202.097248 Y249.094235 Z20 E1310.544864 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X201.768077 Y251.313328 Z20 E1319.87173 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X201.658 Y253.554 Z20 E1329.198595 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X201.768077 Y255.794672 Z20 E1338.525461 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X202.097248 Y258.013765 Z20 E1347.852327 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X202.642344 Y260.189908 Z20 E1357.179192 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X203.398114 Y262.302143 Z20 E1366.506058 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X204.35728 Y264.330129 Z20 E1375.832923 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X205.510605 Y266.254336 Z20 E1385.159789 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X206.846981 Y268.05623 Z20 E1394.486654 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X208.353539 Y269.718461 Z20 E1403.81352 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X210.01577 Y271.225019 Z20 E1413.140385 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X211.817664 Y272.561395 Z20 E1422.467251 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X213.741871 Y273.71472 Z20 E1431.794117 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X215.769857 Y274.673886 Z20 E1441.120982 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X217.882092 Y275.429656 Z20 E1450.447848 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X220.058235 Y275.974752 Z20 E1459.774713 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X222.277328 Y276.303923 Z20 E1469.101579 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X224.518 Y276.414 Z20 E1478.428444 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X226.758672 Y276.303923 Z20 E1487.75531 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X228.977765 Y275.974752 Z20 E1497.082176 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X231.153908 Y275.429656 Z20 E1506.409041 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X233.266143 Y274.673886 Z20 E1515.735907 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X235.294129 Y273.71472 Z20 E1525.062772 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X237.218336 Y272.561395 Z20 E1534.389638 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X239.02023 Y271.225019 Z20 E1543.716503 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X240.682461 Y269.718461 Z20 E1553.043369 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X242.189019 Y268.05623 Z20 E1562.370235 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X243.525395 Y266.254336 Z20 E1571.6971 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X244.67872 Y264.330129 Z20 E1581.023966 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X245.637886 Y262.302143 Z20 E1590.350831 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X246.393656 Y260.189908 Z20 E1599.677697 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X246.938752 Y258.013765 Z20 E1609.004562 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X247.267923 Y255.794672 Z20 E1618.331428 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X247.378 Y253.554 Z20 E1627.658294 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X247.293107 Y251.825962 Z20 E1634.851306 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X247.267923 Y251.313328 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X246.938752 Y249.094235 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X246.393656 Y246.918092 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0002
G0 X246.393656 Y246.918092 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0003 note=intra-page lift
G0 X239.02023 Y237.189019 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0003 note=intra-page XY
G0 X239.02023 Y237.189019 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0003 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0003
G1 X240.131657 Y236.181681 Z20 E1635.16312 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X240.682461 Y235.682461 Z20 E1635.548761 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X241.19058 Y235.121838 Z20 E1636.098561 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X242.189019 Y234.02023 Z20 E1637.641126 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X242.196913 Y234.009586 Z20 E1637.65763 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X243.090462 Y232.804775 Z20 E1639.840326 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X243.525395 Y232.218336 Z20 E1641.1284 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X243.921192 Y231.557989 Z20 E1642.64665 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X244.67872 Y230.294129 Z20 E1646.010585 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X244.690052 Y230.27017 Z20 E1646.076601 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X245.331385 Y228.914186 Z20 E1650.13018 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X245.637886 Y228.266143 Z20 E1652.287679 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X245.901715 Y227.528792 Z20 E1654.807387 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X246.393656 Y226.153908 Z20 E1659.959684 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X246.403316 Y226.115344 Z20 E1660.108221 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X246.767786 Y224.660297 Z20 E1666.032682 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X246.938752 Y223.977765 Z20 E1668.957988 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X247.267923 Y221.758672 Z20 E1678.284854 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X247.378 Y219.518 Z20 E1687.611719 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X247.267923 Y217.277328 Z20 E1696.938585 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X246.938752 Y215.058235 Z20 E1706.26545 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X246.393656 Y212.882092 Z20 E1715.592316 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X245.637886 Y210.769857 Z20 E1724.919182 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X244.67872 Y208.741871 Z20 E1734.246047 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X243.525395 Y206.817664 Z20 E1743.572913 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X242.189019 Y205.01577 Z20 E1752.899778 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X240.682461 Y203.353539 Z20 E1762.226644 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X239.02023 Y201.846981 Z20 E1771.553509 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X237.218336 Y200.510605 Z20 E1780.880375 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X235.294129 Y199.35728 Z20 E1790.207241 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X233.266143 Y198.398114 Z20 E1799.534106 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X231.153908 Y197.642344 Z20 E1808.860972 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X228.977765 Y197.097248 Z20 E1818.187837 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X226.758672 Y196.768077 Z20 E1827.514703 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X224.518 Y196.658 Z20 E1836.841568 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X222.277328 Y196.768077 Z20 E1846.168434 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X220.058235 Y197.097248 Z20 E1855.4953 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X217.882092 Y197.642344 Z20 E1864.822165 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X215.769857 Y198.398114 Z20 E1874.149031 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X213.741871 Y199.35728 Z20 E1883.475896 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X211.817664 Y200.510605 Z20 E1892.802762 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X210.01577 Y201.846981 Z20 E1902.129627 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X208.353539 Y203.353539 Z20 E1911.456493 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X206.846981 Y205.01577 Z20 E1920.783358 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X205.510605 Y206.817664 Z20 E1930.110224 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X204.35728 Y208.741871 Z20 E1939.43709 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X203.398114 Y210.769857 Z20 E1948.763955 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X202.642344 Y212.882092 Z20 E1958.090821 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X202.097248 Y215.058235 Z20 E1967.417686 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X201.768077 Y217.277328 Z20 E1976.744552 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X201.658 Y219.518 Z20 E1986.071417 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X201.768077 Y221.758672 Z20 E1995.398283 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X202.097248 Y223.977765 Z20 E2004.725149 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X202.642344 Y226.153908 Z20 E2014.052014 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X203.398114 Y228.266143 Z20 E2023.37888 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X204.35728 Y230.294129 Z20 E2032.705745 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X205.510605 Y232.218336 Z20 E2042.032611 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X206.846981 Y234.02023 Z20 E2051.359476 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X208.353539 Y235.682461 Z20 E2060.686342 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X210.01577 Y237.189019 Z20 E2070.013208 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X211.817664 Y238.525395 Z20 E2079.340073 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X213.741871 Y239.67872 Z20 E2088.666939 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X215.769857 Y240.637886 Z20 E2097.993804 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X217.882092 Y241.393656 Z20 E2107.32067 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X220.058235 Y241.938752 Z20 E2116.647535 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X222.277328 Y242.267923 Z20 E2125.974401 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X224.518 Y242.378 Z20 E2135.301267 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X226.758672 Y242.267923 Z20 E2144.628132 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X228.977765 Y241.938752 Z20 E2153.954998 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X231.153908 Y241.393656 Z20 E2163.281863 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X233.266143 Y240.637886 Z20 E2172.608729 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X234.830155 Y239.898164 Z20 E2179.801741 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X235.294129 Y239.67872 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X237.218336 Y238.525395 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X239.02023 Y237.189019 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0003
G0 X239.02023 Y237.189019 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0004 note=intra-page lift
G0 X212.29769 Y246.750497 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0004 note=intra-page XY
G0 X212.29769 Y246.750497 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0004 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0004
G1 X211.792355 Y245.338181 Z20 E2180.113555 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X211.601886 Y244.805857 Z20 E2180.392908 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X211.202282 Y243.960964 Z20 E2181.048996 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X210.64272 Y242.777871 Z20 E2182.374594 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X210.544397 Y242.613828 Z20 E2182.608065 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X209.773243 Y241.327235 Z20 E2184.790761 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X209.489395 Y240.853664 Z20 E2185.751189 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X208.924745 Y240.092322 Z20 E2187.597085 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X208.153019 Y239.05177 Z20 E2190.522695 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X208.015682 Y238.900242 Z20 E2191.027037 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X207.008344 Y237.788815 Z20 E2195.080616 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X206.646461 Y237.389539 Z20 E2196.68911 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X205.934311 Y236.744083 Z20 E2199.757822 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X204.98423 Y235.882981 Z20 E2204.250436 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X204.809327 Y235.753264 Z20 E2205.058656 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X203.604516 Y234.859715 Z20 E2210.983118 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X203.182336 Y234.546605 Z20 E2213.168384 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X201.258129 Y233.39328 Z20 E2222.495249 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X199.230143 Y232.434114 Z20 E2231.822115 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X197.117908 Y231.678344 Z20 E2241.14898 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X194.941765 Y231.133248 Z20 E2250.475846 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X192.722672 Y230.804077 Z20 E2259.802711 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X190.482 Y230.694 Z20 E2269.129577 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X188.241328 Y230.804077 Z20 E2278.456443 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X186.022235 Y231.133248 Z20 E2287.783308 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X183.846092 Y231.678344 Z20 E2297.110174 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X181.733857 Y232.434114 Z20 E2306.437039 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X179.705871 Y233.39328 Z20 E2315.763905 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X177.781664 Y234.546605 Z20 E2325.09077 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X175.97977 Y235.882981 Z20 E2334.417636 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X174.317539 Y237.389539 Z20 E2343.744501 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X172.810981 Y239.05177 Z20 E2353.071367 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X171.474605 Y240.853664 Z20 E2362.398233 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X170.32128 Y242.777871 Z20 E2371.725098 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X169.362114 Y244.805857 Z20 E2381.051964 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X168.606344 Y246.918092 Z20 E2390.378829 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X168.061248 Y249.094235 Z20 E2399.705695 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X167.732077 Y251.313328 Z20 E2409.03256 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X167.622 Y253.554 Z20 E2418.359426 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X167.732077 Y255.794672 Z20 E2427.686292 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X168.061248 Y258.013765 Z20 E2437.013157 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X168.606344 Y260.189908 Z20 E2446.340023 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X169.362114 Y262.302143 Z20 E2455.666888 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X170.32128 Y264.330129 Z20 E2464.993754 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X171.474605 Y266.254336 Z20 E2474.320619 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X172.810981 Y268.05623 Z20 E2483.647485 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X174.317539 Y269.718461 Z20 E2492.974351 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X175.97977 Y271.225019 Z20 E2502.301216 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X177.781664 Y272.561395 Z20 E2511.628082 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X179.705871 Y273.71472 Z20 E2520.954947 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X181.733857 Y274.673886 Z20 E2530.281813 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X183.846092 Y275.429656 Z20 E2539.608678 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X186.022235 Y275.974752 Z20 E2548.935544 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X188.241328 Y276.303923 Z20 E2558.26241 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X190.482 Y276.414 Z20 E2567.589275 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X192.722672 Y276.303923 Z20 E2576.916141 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X194.941765 Y275.974752 Z20 E2586.243006 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X197.117908 Y275.429656 Z20 E2595.569872 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X199.230143 Y274.673886 Z20 E2604.896737 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X201.258129 Y273.71472 Z20 E2614.223603 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X203.182336 Y272.561395 Z20 E2623.550468 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X204.98423 Y271.225019 Z20 E2632.877334 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X206.646461 Y269.718461 Z20 E2642.2042 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X208.153019 Y268.05623 Z20 E2651.531065 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X209.489395 Y266.254336 Z20 E2660.857931 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X210.64272 Y264.330129 Z20 E2670.184796 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X211.601886 Y262.302143 Z20 E2679.511662 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X212.357656 Y260.189908 Z20 E2688.838527 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X212.902752 Y258.013765 Z20 E2698.165393 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X213.231923 Y255.794672 Z20 E2707.492259 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X213.342 Y253.554 Z20 E2716.819124 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X213.248373 Y251.648176 Z20 E2724.752176 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X213.231923 Y251.313328 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X212.902752 Y249.094235 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X212.357656 Y246.918092 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X212.29769 Y246.750497 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0004
G0 X212.29769 Y246.750497 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0005 note=intra-page lift
G0 X204.98423 Y237.189019 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0005 note=intra-page XY
G0 X204.98423 Y237.189019 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0005 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0005
G1 X206.095657 Y236.181681 Z20 E2725.06399 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X206.646461 Y235.682461 Z20 E2725.449631 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X207.15458 Y235.121838 Z20 E2725.999431 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X208.153019 Y234.02023 Z20 E2727.541996 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X208.160913 Y234.009586 Z20 E2727.5585 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X209.054462 Y232.804775 Z20 E2729.741197 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X209.489395 Y232.218336 Z20 E2731.029271 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X209.885192 Y231.557989 Z20 E2732.547521 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X210.64272 Y230.294129 Z20 E2735.911456 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X210.654052 Y230.27017 Z20 E2735.977472 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X211.295385 Y228.914186 Z20 E2740.031051 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X211.601886 Y228.266143 Z20 E2742.18855 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X211.865715 Y227.528792 Z20 E2744.708257 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X212.357656 Y226.153908 Z20 E2749.860554 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X212.367316 Y226.115344 Z20 E2750.009091 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X212.731786 Y224.660297 Z20 E2755.933553 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X212.902752 Y223.977765 Z20 E2758.858859 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X213.231923 Y221.758672 Z20 E2768.185724 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X213.342 Y219.518 Z20 E2777.51259 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X213.231923 Y217.277328 Z20 E2786.839455 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X212.902752 Y215.058235 Z20 E2796.166321 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X212.357656 Y212.882092 Z20 E2805.493187 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X211.601886 Y210.769857 Z20 E2814.820052 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X210.64272 Y208.741871 Z20 E2824.146918 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X209.489395 Y206.817664 Z20 E2833.473783 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X208.153019 Y205.01577 Z20 E2842.800649 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X206.646461 Y203.353539 Z20 E2852.127514 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X204.98423 Y201.846981 Z20 E2861.45438 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X203.182336 Y200.510605 Z20 E2870.781246 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X201.258129 Y199.35728 Z20 E2880.108111 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X199.230143 Y198.398114 Z20 E2889.434977 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X197.117908 Y197.642344 Z20 E2898.761842 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X194.941765 Y197.097248 Z20 E2908.088708 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X192.722672 Y196.768077 Z20 E2917.415573 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X190.482 Y196.658 Z20 E2926.742439 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X188.241328 Y196.768077 Z20 E2936.069305 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X186.022235 Y197.097248 Z20 E2945.39617 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X183.846092 Y197.642344 Z20 E2954.723036 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X181.733857 Y198.398114 Z20 E2964.049901 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X179.705871 Y199.35728 Z20 E2973.376767 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X177.781664 Y200.510605 Z20 E2982.703632 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X175.97977 Y201.846981 Z20 E2992.030498 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X174.317539 Y203.353539 Z20 E3001.357363 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X172.810981 Y205.01577 Z20 E3010.684229 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X171.474605 Y206.817664 Z20 E3020.011095 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X170.32128 Y208.741871 Z20 E3029.33796 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X169.362114 Y210.769857 Z20 E3038.664826 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X168.606344 Y212.882092 Z20 E3047.991691 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X168.061248 Y215.058235 Z20 E3057.318557 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X167.732077 Y217.277328 Z20 E3066.645422 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X167.622 Y219.518 Z20 E3075.972288 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X167.732077 Y221.758672 Z20 E3085.299154 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X168.061248 Y223.977765 Z20 E3094.626019 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X168.606344 Y226.153908 Z20 E3103.952885 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X169.362114 Y228.266143 Z20 E3113.27975 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X170.32128 Y230.294129 Z20 E3122.606616 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X171.474605 Y232.218336 Z20 E3131.933481 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X172.810981 Y234.02023 Z20 E3141.260347 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X174.317539 Y235.682461 Z20 E3150.587213 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X175.97977 Y237.189019 Z20 E3159.914078 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X177.781664 Y238.525395 Z20 E3169.240944 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X179.705871 Y239.67872 Z20 E3178.567809 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X181.733857 Y240.637886 Z20 E3187.894675 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X183.846092 Y241.393656 Z20 E3197.22154 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X186.022235 Y241.938752 Z20 E3206.548406 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X188.241328 Y242.267923 Z20 E3215.875272 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X190.482 Y242.378 Z20 E3225.202137 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X192.722672 Y242.267923 Z20 E3234.529003 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X194.941765 Y241.938752 Z20 E3243.855868 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X197.117908 Y241.393656 Z20 E3253.182734 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X199.230143 Y240.637886 Z20 E3262.509599 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X200.794155 Y239.898164 Z20 E3269.702612 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X201.258129 Y239.67872 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
G1 X203.182336 Y238.525395 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
G1 X204.98423 Y237.189019 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0005
G0 X204.98423 Y237.189019 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0006 note=intra-page lift
G0 X178.26169 Y246.750497 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0006 note=intra-page XY
G0 X178.26169 Y246.750497 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0006 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0006
G1 X177.756355 Y245.338181 Z20 E3270.014425 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X177.565886 Y244.805857 Z20 E3270.293778 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X177.166282 Y243.960964 Z20 E3270.949867 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X176.60672 Y242.777871 Z20 E3272.275464 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X176.508397 Y242.613828 Z20 E3272.508936 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X175.737243 Y241.327235 Z20 E3274.691632 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X175.453395 Y240.853664 Z20 E3275.65206 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X174.888745 Y240.092322 Z20 E3277.497956 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X174.117019 Y239.05177 Z20 E3280.423565 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X173.979682 Y238.900242 Z20 E3280.927907 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X172.972344 Y237.788815 Z20 E3284.981486 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X172.610461 Y237.389539 Z20 E3286.589981 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X171.898311 Y236.744083 Z20 E3289.658693 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X170.94823 Y235.882981 Z20 E3294.151306 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X170.773327 Y235.753264 Z20 E3294.959527 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X169.568516 Y234.859715 Z20 E3300.883988 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X169.146336 Y234.546605 Z20 E3303.069254 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X167.222129 Y233.39328 Z20 E3312.39612 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X165.194143 Y232.434114 Z20 E3321.722985 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X163.081908 Y231.678344 Z20 E3331.049851 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X160.905765 Y231.133248 Z20 E3340.376716 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X158.686672 Y230.804077 Z20 E3349.703582 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X156.446 Y230.694 Z20 E3359.030448 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X154.205328 Y230.804077 Z20 E3368.357313 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X151.986235 Y231.133248 Z20 E3377.684179 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X149.810092 Y231.678344 Z20 E3387.011044 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X147.697857 Y232.434114 Z20 E3396.33791 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X145.669871 Y233.39328 Z20 E3405.664775 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X143.745664 Y234.546605 Z20 E3414.991641 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X141.94377 Y235.882981 Z20 E3424.318506 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X140.281539 Y237.389539 Z20 E3433.645372 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X138.774981 Y239.05177 Z20 E3442.972238 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X137.438605 Y240.853664 Z20 E3452.299103 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X136.28528 Y242.777871 Z20 E3461.625969 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X135.326114 Y244.805857 Z20 E3470.952834 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X134.570344 Y246.918092 Z20 E3480.2797 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X134.025248 Y249.094235 Z20 E3489.606565 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X133.696077 Y251.313328 Z20 E3498.933431 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X133.586 Y253.554 Z20 E3508.260297 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X133.696077 Y255.794672 Z20 E3517.587162 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X134.025248 Y258.013765 Z20 E3526.914028 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X134.570344 Y260.189908 Z20 E3536.240893 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X135.326114 Y262.302143 Z20 E3545.567759 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X136.28528 Y264.330129 Z20 E3554.894624 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X137.438605 Y266.254336 Z20 E3564.22149 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X138.774981 Y268.05623 Z20 E3573.548356 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X140.281539 Y269.718461 Z20 E3582.875221 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X141.94377 Y271.225019 Z20 E3592.202087 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X143.745664 Y272.561395 Z20 E3601.528952 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X145.669871 Y273.71472 Z20 E3610.855818 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X147.697857 Y274.673886 Z20 E3620.182683 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X149.810092 Y275.429656 Z20 E3629.509549 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X151.986235 Y275.974752 Z20 E3638.836415 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X154.205328 Y276.303923 Z20 E3648.16328 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X156.446 Y276.414 Z20 E3657.490146 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X158.686672 Y276.303923 Z20 E3666.817011 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X160.905765 Y275.974752 Z20 E3676.143877 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X163.081908 Y275.429656 Z20 E3685.470742 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X165.194143 Y274.673886 Z20 E3694.797608 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X167.222129 Y273.71472 Z20 E3704.124473 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X169.146336 Y272.561395 Z20 E3713.451339 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X170.94823 Y271.225019 Z20 E3722.778205 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X172.610461 Y269.718461 Z20 E3732.10507 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X174.117019 Y268.05623 Z20 E3741.431936 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X175.453395 Y266.254336 Z20 E3750.758801 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X176.60672 Y264.330129 Z20 E3760.085667 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X177.565886 Y262.302143 Z20 E3769.412532 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X178.321656 Y260.189908 Z20 E3778.739398 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X178.866752 Y258.013765 Z20 E3788.066264 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X179.195923 Y255.794672 Z20 E3797.393129 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X179.306 Y253.554 Z20 E3806.719995 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X179.212373 Y251.648176 Z20 E3814.653047 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X179.195923 Y251.313328 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X178.866752 Y249.094235 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X178.321656 Y246.918092 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X178.26169 Y246.750497 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0006
G0 X178.26169 Y246.750497 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0007 note=intra-page lift
G0 X170.94823 Y237.189019 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0007 note=intra-page XY
G0 X170.94823 Y237.189019 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0007 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0007
G1 X172.059657 Y236.181681 Z20 E3814.964861 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X172.610461 Y235.682461 Z20 E3815.350502 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X173.11858 Y235.121838 Z20 E3815.900302 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X174.117019 Y234.02023 Z20 E3817.442867 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X174.124913 Y234.009586 Z20 E3817.459371 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X175.018462 Y232.804775 Z20 E3819.642067 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X175.453395 Y232.218336 Z20 E3820.930141 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X175.849192 Y231.557989 Z20 E3822.448391 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X176.60672 Y230.294129 Z20 E3825.812326 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X176.618052 Y230.27017 Z20 E3825.878342 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X177.259385 Y228.914186 Z20 E3829.931921 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X177.565886 Y228.266143 Z20 E3832.089421 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X177.829715 Y227.528792 Z20 E3834.609128 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X178.321656 Y226.153908 Z20 E3839.761425 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X178.331316 Y226.115344 Z20 E3839.909962 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X178.695786 Y224.660297 Z20 E3845.834424 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X178.866752 Y223.977765 Z20 E3848.759729 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X179.195923 Y221.758672 Z20 E3858.086595 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X179.306 Y219.518 Z20 E3867.41346 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X179.195923 Y217.277328 Z20 E3876.740326 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X178.866752 Y215.058235 Z20 E3886.067192 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X178.321656 Y212.882092 Z20 E3895.394057 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X177.565886 Y210.769857 Z20 E3904.720923 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X176.60672 Y208.741871 Z20 E3914.047788 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X175.453395 Y206.817664 Z20 E3923.374654 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X174.117019 Y205.01577 Z20 E3932.701519 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X172.610461 Y203.353539 Z20 E3942.028385 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X170.94823 Y201.846981 Z20 E3951.355251 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X169.146336 Y200.510605 Z20 E3960.682116 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X167.222129 Y199.35728 Z20 E3970.008982 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X165.194143 Y198.398114 Z20 E3979.335847 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X163.081908 Y197.642344 Z20 E3988.662713 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X160.905765 Y197.097248 Z20 E3997.989578 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X158.686672 Y196.768077 Z20 E4007.316444 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X156.446 Y196.658 Z20 E4016.643309 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X154.205328 Y196.768077 Z20 E4025.970175 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X151.986235 Y197.097248 Z20 E4035.297041 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X149.810092 Y197.642344 Z20 E4044.623906 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X147.697857 Y198.398114 Z20 E4053.950772 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X145.669871 Y199.35728 Z20 E4063.277637 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X143.745664 Y200.510605 Z20 E4072.604503 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X141.94377 Y201.846981 Z20 E4081.931368 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X140.281539 Y203.353539 Z20 E4091.258234 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X138.774981 Y205.01577 Z20 E4100.5851 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X137.438605 Y206.817664 Z20 E4109.911965 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X136.28528 Y208.741871 Z20 E4119.238831 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X135.326114 Y210.769857 Z20 E4128.565696 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X134.570344 Y212.882092 Z20 E4137.892562 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X134.025248 Y215.058235 Z20 E4147.219427 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X133.696077 Y217.277328 Z20 E4156.546293 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X133.586 Y219.518 Z20 E4165.873159 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X133.696077 Y221.758672 Z20 E4175.200024 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X134.025248 Y223.977765 Z20 E4184.52689 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X134.570344 Y226.153908 Z20 E4193.853755 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X135.326114 Y228.266143 Z20 E4203.180621 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X136.28528 Y230.294129 Z20 E4212.507486 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X137.438605 Y232.218336 Z20 E4221.834352 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X138.774981 Y234.02023 Z20 E4231.161218 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X140.281539 Y235.682461 Z20 E4240.488083 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X141.94377 Y237.189019 Z20 E4249.814949 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X143.745664 Y238.525395 Z20 E4259.141814 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X145.669871 Y239.67872 Z20 E4268.46868 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X147.697857 Y240.637886 Z20 E4277.795545 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X149.810092 Y241.393656 Z20 E4287.122411 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X151.986235 Y241.938752 Z20 E4296.449276 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X154.205328 Y242.267923 Z20 E4305.776142 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X156.446 Y242.378 Z20 E4315.103008 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X158.686672 Y242.267923 Z20 E4324.429873 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X160.905765 Y241.938752 Z20 E4333.756739 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X163.081908 Y241.393656 Z20 E4343.083604 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X165.194143 Y240.637886 Z20 E4352.41047 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X166.758155 Y239.898164 Z20 E4359.603482 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X167.222129 Y239.67872 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
G1 X169.146336 Y238.525395 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
G1 X170.94823 Y237.189019 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0007
G0 X170.94823 Y237.189019 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0008 note=intra-page lift
G0 X163.081908 Y207.357656 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0008 note=intra-page XY
G0 X163.081908 Y207.357656 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0008 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0008
G1 X164.494224 Y206.852321 Z20 E4359.915296 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X165.194143 Y206.601886 Z20 E4360.300937 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X165.878125 Y206.278387 Z20 E4360.850737 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X167.222129 Y205.64272 Z20 E4362.393302 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X167.233496 Y205.635907 Z20 E4362.409806 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X168.520089 Y204.864753 Z20 E4364.592502 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X169.146336 Y204.489395 Z20 E4365.880577 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X169.764707 Y204.03078 Z20 E4367.398826 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X170.94823 Y203.153019 Z20 E4370.762761 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X170.967868 Y203.13522 Z20 E4370.828778 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X172.079295 Y202.127882 Z20 E4374.882357 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X172.610461 Y201.646461 Z20 E4377.039856 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X173.136379 Y201.0662 Z20 E4379.559563 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X174.117019 Y199.98423 Z20 E4384.71186 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X174.140701 Y199.952298 Z20 E4384.860397 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X175.03425 Y198.747487 Z20 E4390.784859 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X175.453395 Y198.182336 Z20 E4393.710165 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X176.60672 Y196.258129 Z20 E4403.03703 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X177.565886 Y194.230143 Z20 E4412.363896 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X178.321656 Y192.117908 Z20 E4421.690761 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X178.866752 Y189.941765 Z20 E4431.017627 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X179.195923 Y187.722672 Z20 E4440.344492 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X179.306 Y185.482 Z20 E4449.671358 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X179.195923 Y183.241328 Z20 E4458.998224 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X178.866752 Y181.022235 Z20 E4468.325089 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X178.321656 Y178.846092 Z20 E4477.651955 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X177.565886 Y176.733857 Z20 E4486.97882 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X176.60672 Y174.705871 Z20 E4496.305686 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X175.453395 Y172.781664 Z20 E4505.632551 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X174.117019 Y170.97977 Z20 E4514.959417 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X172.610461 Y169.317539 Z20 E4524.286282 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X170.94823 Y167.810981 Z20 E4533.613148 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X169.146336 Y166.474605 Z20 E4542.940014 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X167.222129 Y165.32128 Z20 E4552.266879 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X165.194143 Y164.362114 Z20 E4561.593745 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X163.081908 Y163.606344 Z20 E4570.92061 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X160.905765 Y163.061248 Z20 E4580.247476 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X158.686672 Y162.732077 Z20 E4589.574341 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X156.446 Y162.622 Z20 E4598.901207 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X154.205328 Y162.732077 Z20 E4608.228073 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X151.986235 Y163.061248 Z20 E4617.554938 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X149.810092 Y163.606344 Z20 E4626.881804 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X147.697857 Y164.362114 Z20 E4636.208669 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X145.669871 Y165.32128 Z20 E4645.535535 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X143.745664 Y166.474605 Z20 E4654.8624 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X141.94377 Y167.810981 Z20 E4664.189266 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X140.281539 Y169.317539 Z20 E4673.516132 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X138.774981 Y170.97977 Z20 E4682.842997 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X137.438605 Y172.781664 Z20 E4692.169863 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X136.28528 Y174.705871 Z20 E4701.496728 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X135.326114 Y176.733857 Z20 E4710.823594 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X134.570344 Y178.846092 Z20 E4720.150459 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X134.025248 Y181.022235 Z20 E4729.477325 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X133.696077 Y183.241328 Z20 E4738.804191 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X133.586 Y185.482 Z20 E4748.131056 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X133.696077 Y187.722672 Z20 E4757.457922 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X134.025248 Y189.941765 Z20 E4766.784787 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X134.570344 Y192.117908 Z20 E4776.111653 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X135.326114 Y194.230143 Z20 E4785.438518 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X136.28528 Y196.258129 Z20 E4794.765384 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X137.438605 Y198.182336 Z20 E4804.09225 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X138.774981 Y199.98423 Z20 E4813.419115 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X140.281539 Y201.646461 Z20 E4822.745981 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X141.94377 Y203.153019 Z20 E4832.072846 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X143.745664 Y204.489395 Z20 E4841.399712 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X145.669871 Y205.64272 Z20 E4850.726577 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X147.697857 Y206.601886 Z20 E4860.053443 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X149.810092 Y207.357656 Z20 E4869.380308 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X151.986235 Y207.902752 Z20 E4878.707174 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X154.205328 Y208.231923 Z20 E4888.03404 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X156.446 Y208.342 Z20 E4897.360905 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X158.174038 Y208.257107 Z20 E4904.553917 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X158.686672 Y208.231923 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X160.905765 Y207.902752 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X163.081908 Y207.357656 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0008
G0 X163.081908 Y207.357656 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0009 note=intra-page lift
G0 X172.810981 Y199.98423 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0009 note=intra-page XY
G0 X172.810981 Y199.98423 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0009 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0009
G1 X173.818319 Y201.095657 Z20 E4904.865731 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X174.317539 Y201.646461 Z20 E4905.251372 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X174.878162 Y202.15458 Z20 E4905.801173 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X175.97977 Y203.153019 Z20 E4907.343737 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X175.990414 Y203.160913 Z20 E4907.360241 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X177.195225 Y204.054462 Z20 E4909.542938 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X177.781664 Y204.489395 Z20 E4910.831012 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X178.442011 Y204.885192 Z20 E4912.349262 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X179.705871 Y205.64272 Z20 E4915.713197 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X179.72983 Y205.654052 Z20 E4915.779213 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X181.085814 Y206.295385 Z20 E4919.832792 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X181.733857 Y206.601886 Z20 E4921.990291 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X182.471208 Y206.865715 Z20 E4924.509998 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X183.846092 Y207.357656 Z20 E4929.662296 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X183.884656 Y207.367316 Z20 E4929.810833 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X185.339703 Y207.731786 Z20 E4935.735294 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X186.022235 Y207.902752 Z20 E4938.6606 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X188.241328 Y208.231923 Z20 E4947.987465 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X190.482 Y208.342 Z20 E4957.314331 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X192.722672 Y208.231923 Z20 E4966.641197 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X194.941765 Y207.902752 Z20 E4975.968062 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X197.117908 Y207.357656 Z20 E4985.294928 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X199.230143 Y206.601886 Z20 E4994.621793 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X201.258129 Y205.64272 Z20 E5003.948659 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X203.182336 Y204.489395 Z20 E5013.275524 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X204.98423 Y203.153019 Z20 E5022.60239 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X206.646461 Y201.646461 Z20 E5031.929256 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X208.153019 Y199.98423 Z20 E5041.256121 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X209.489395 Y198.182336 Z20 E5050.582987 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X210.64272 Y196.258129 Z20 E5059.909852 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X211.601886 Y194.230143 Z20 E5069.236718 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X212.357656 Y192.117908 Z20 E5078.563583 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X212.902752 Y189.941765 Z20 E5087.890449 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X213.231923 Y187.722672 Z20 E5097.217314 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X213.342 Y185.482 Z20 E5106.54418 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X213.231923 Y183.241328 Z20 E5115.871046 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X212.902752 Y181.022235 Z20 E5125.197911 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X212.357656 Y178.846092 Z20 E5134.524777 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X211.601886 Y176.733857 Z20 E5143.851642 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X210.64272 Y174.705871 Z20 E5153.178508 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X209.489395 Y172.781664 Z20 E5162.505373 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X208.153019 Y170.97977 Z20 E5171.832239 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X206.646461 Y169.317539 Z20 E5181.159105 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X204.98423 Y167.810981 Z20 E5190.48597 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X203.182336 Y166.474605 Z20 E5199.812836 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X201.258129 Y165.32128 Z20 E5209.139701 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X199.230143 Y164.362114 Z20 E5218.466567 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X197.117908 Y163.606344 Z20 E5227.793432 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X194.941765 Y163.061248 Z20 E5237.120298 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X192.722672 Y162.732077 Z20 E5246.447164 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X190.482 Y162.622 Z20 E5255.774029 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X188.241328 Y162.732077 Z20 E5265.100895 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X186.022235 Y163.061248 Z20 E5274.42776 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X183.846092 Y163.606344 Z20 E5283.754626 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X181.733857 Y164.362114 Z20 E5293.081491 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X179.705871 Y165.32128 Z20 E5302.408357 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X177.781664 Y166.474605 Z20 E5311.735223 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X175.97977 Y167.810981 Z20 E5321.062088 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X174.317539 Y169.317539 Z20 E5330.388954 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X172.810981 Y170.97977 Z20 E5339.715819 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X171.474605 Y172.781664 Z20 E5349.042685 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X170.32128 Y174.705871 Z20 E5358.36955 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X169.362114 Y176.733857 Z20 E5367.696416 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X168.606344 Y178.846092 Z20 E5377.023281 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X168.061248 Y181.022235 Z20 E5386.350147 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X167.732077 Y183.241328 Z20 E5395.677013 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X167.622 Y185.482 Z20 E5405.003878 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X167.732077 Y187.722672 Z20 E5414.330744 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X168.061248 Y189.941765 Z20 E5423.657609 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X168.606344 Y192.117908 Z20 E5432.984475 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X169.362114 Y194.230143 Z20 E5442.31134 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X170.101836 Y195.794155 Z20 E5449.504353 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X170.32128 Y196.258129 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X171.474605 Y198.182336 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X172.810981 Y199.98423 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0009
G0 X172.810981 Y199.98423 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0010 note=intra-page lift
G0 X163.249503 Y173.26169 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0010 note=intra-page XY
G0 X163.249503 Y173.26169 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0010 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0010
G1 X164.661819 Y172.756355 Z20 E5449.816167 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X165.194143 Y172.565886 Z20 E5450.09552 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X166.039036 Y172.166282 Z20 E5450.751608 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X167.222129 Y171.60672 Z20 E5452.077205 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X167.386172 Y171.508397 Z20 E5452.310677 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X168.672765 Y170.737243 Z20 E5454.493373 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X169.146336 Y170.453395 Z20 E5455.453801 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X169.907678 Y169.888745 Z20 E5457.299697 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X170.94823 Y169.117019 Z20 E5460.225306 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X171.099758 Y168.979682 Z20 E5460.729648 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X172.211185 Y167.972344 Z20 E5464.783227 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X172.610461 Y167.610461 Z20 E5466.391722 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X173.255917 Y166.898311 Z20 E5469.460434 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X174.117019 Y165.94823 Z20 E5473.953047 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X174.246736 Y165.773327 Z20 E5474.761268 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X175.140285 Y164.568516 Z20 E5480.685729 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X175.453395 Y164.146336 Z20 E5482.870995 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X176.60672 Y162.222129 Z20 E5492.197861 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X177.565886 Y160.194143 Z20 E5501.524726 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X178.321656 Y158.081908 Z20 E5510.851592 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X178.866752 Y155.905765 Z20 E5520.178457 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X179.195923 Y153.686672 Z20 E5529.505323 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X179.306 Y151.446 Z20 E5538.832189 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X179.195923 Y149.205328 Z20 E5548.159054 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X178.866752 Y146.986235 Z20 E5557.48592 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X178.321656 Y144.810092 Z20 E5566.812785 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X177.565886 Y142.697857 Z20 E5576.139651 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X176.60672 Y140.669871 Z20 E5585.466516 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X175.453395 Y138.745664 Z20 E5594.793382 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X174.117019 Y136.94377 Z20 E5604.120248 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X172.610461 Y135.281539 Z20 E5613.447113 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X170.94823 Y133.774981 Z20 E5622.773979 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X169.146336 Y132.438605 Z20 E5632.100844 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X167.222129 Y131.28528 Z20 E5641.42771 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X165.194143 Y130.326114 Z20 E5650.754575 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X163.081908 Y129.570344 Z20 E5660.081441 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X160.905765 Y129.025248 Z20 E5669.408307 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X158.686672 Y128.696077 Z20 E5678.735172 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X156.446 Y128.586 Z20 E5688.062038 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X154.205328 Y128.696077 Z20 E5697.388903 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X151.986235 Y129.025248 Z20 E5706.715769 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X149.810092 Y129.570344 Z20 E5716.042634 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X147.697857 Y130.326114 Z20 E5725.3695 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X145.669871 Y131.28528 Z20 E5734.696366 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X143.745664 Y132.438605 Z20 E5744.023231 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X141.94377 Y133.774981 Z20 E5753.350097 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X140.281539 Y135.281539 Z20 E5762.676962 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X138.774981 Y136.94377 Z20 E5772.003828 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X137.438605 Y138.745664 Z20 E5781.330693 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X136.28528 Y140.669871 Z20 E5790.657559 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X135.326114 Y142.697857 Z20 E5799.984424 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X134.570344 Y144.810092 Z20 E5809.31129 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X134.025248 Y146.986235 Z20 E5818.638156 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X133.696077 Y149.205328 Z20 E5827.965021 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X133.586 Y151.446 Z20 E5837.291887 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X133.696077 Y153.686672 Z20 E5846.618752 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X134.025248 Y155.905765 Z20 E5855.945618 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X134.570344 Y158.081908 Z20 E5865.272483 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X135.326114 Y160.194143 Z20 E5874.599349 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X136.28528 Y162.222129 Z20 E5883.926215 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X137.438605 Y164.146336 Z20 E5893.25308 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X138.774981 Y165.94823 Z20 E5902.579946 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X140.281539 Y167.610461 Z20 E5911.906811 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X141.94377 Y169.117019 Z20 E5921.233677 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X143.745664 Y170.453395 Z20 E5930.560542 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X145.669871 Y171.60672 Z20 E5939.887408 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X147.697857 Y172.565886 Z20 E5949.214274 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X149.810092 Y173.321656 Z20 E5958.541139 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X151.986235 Y173.866752 Z20 E5967.868005 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X154.205328 Y174.195923 Z20 E5977.19487 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X156.446 Y174.306 Z20 E5986.521736 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X158.351824 Y174.212373 Z20 E5994.454788 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X158.686672 Y174.195923 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X160.905765 Y173.866752 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X163.081908 Y173.321656 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X163.249503 Y173.26169 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0010
G0 X163.249503 Y173.26169 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0011 note=intra-page lift
G0 X172.810981 Y165.94823 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0011 note=intra-page XY
G0 X172.810981 Y165.94823 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0011 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0011
G1 X173.818319 Y167.059657 Z20 E5994.766602 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X174.317539 Y167.610461 Z20 E5995.152243 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X174.878162 Y168.11858 Z20 E5995.702043 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X175.97977 Y169.117019 Z20 E5997.244608 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X175.990414 Y169.124913 Z20 E5997.261112 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X177.195225 Y170.018462 Z20 E5999.443808 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X177.781664 Y170.453395 Z20 E6000.731883 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X178.442011 Y170.849192 Z20 E6002.250132 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X179.705871 Y171.60672 Z20 E6005.614067 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X179.72983 Y171.618052 Z20 E6005.680084 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X181.085814 Y172.259385 Z20 E6009.733663 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X181.733857 Y172.565886 Z20 E6011.891162 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X182.471208 Y172.829715 Z20 E6014.410869 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X183.846092 Y173.321656 Z20 E6019.563166 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X183.884656 Y173.331316 Z20 E6019.711703 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X185.339703 Y173.695786 Z20 E6025.636165 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X186.022235 Y173.866752 Z20 E6028.56147 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X188.241328 Y174.195923 Z20 E6037.888336 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X190.482 Y174.306 Z20 E6047.215202 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X192.722672 Y174.195923 Z20 E6056.542067 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X194.941765 Y173.866752 Z20 E6065.868933 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X197.117908 Y173.321656 Z20 E6075.195798 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X199.230143 Y172.565886 Z20 E6084.522664 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X201.258129 Y171.60672 Z20 E6093.849529 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X203.182336 Y170.453395 Z20 E6103.176395 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X204.98423 Y169.117019 Z20 E6112.50326 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X206.646461 Y167.610461 Z20 E6121.830126 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X208.153019 Y165.94823 Z20 E6131.156992 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X209.489395 Y164.146336 Z20 E6140.483857 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X210.64272 Y162.222129 Z20 E6149.810723 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X211.601886 Y160.194143 Z20 E6159.137588 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X212.357656 Y158.081908 Z20 E6168.464454 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X212.902752 Y155.905765 Z20 E6177.791319 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X213.231923 Y153.686672 Z20 E6187.118185 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X213.342 Y151.446 Z20 E6196.445051 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X213.231923 Y149.205328 Z20 E6205.771916 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X212.902752 Y146.986235 Z20 E6215.098782 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X212.357656 Y144.810092 Z20 E6224.425647 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X211.601886 Y142.697857 Z20 E6233.752513 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X210.64272 Y140.669871 Z20 E6243.079378 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X209.489395 Y138.745664 Z20 E6252.406244 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X208.153019 Y136.94377 Z20 E6261.73311 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X206.646461 Y135.281539 Z20 E6271.059975 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X204.98423 Y133.774981 Z20 E6280.386841 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X203.182336 Y132.438605 Z20 E6289.713706 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X201.258129 Y131.28528 Z20 E6299.040572 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X199.230143 Y130.326114 Z20 E6308.367437 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X197.117908 Y129.570344 Z20 E6317.694303 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X194.941765 Y129.025248 Z20 E6327.021169 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X192.722672 Y128.696077 Z20 E6336.348034 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X190.482 Y128.586 Z20 E6345.6749 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X188.241328 Y128.696077 Z20 E6355.001765 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X186.022235 Y129.025248 Z20 E6364.328631 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X183.846092 Y129.570344 Z20 E6373.655496 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X181.733857 Y130.326114 Z20 E6382.982362 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X179.705871 Y131.28528 Z20 E6392.309227 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X177.781664 Y132.438605 Z20 E6401.636093 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X175.97977 Y133.774981 Z20 E6410.962959 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X174.317539 Y135.281539 Z20 E6420.289824 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X172.810981 Y136.94377 Z20 E6429.61669 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X171.474605 Y138.745664 Z20 E6438.943555 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X170.32128 Y140.669871 Z20 E6448.270421 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X169.362114 Y142.697857 Z20 E6457.597286 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X168.606344 Y144.810092 Z20 E6466.924152 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X168.061248 Y146.986235 Z20 E6476.251018 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X167.732077 Y149.205328 Z20 E6485.577883 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X167.622 Y151.446 Z20 E6494.904749 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X167.732077 Y153.686672 Z20 E6504.231614 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X168.061248 Y155.905765 Z20 E6513.55848 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X168.606344 Y158.081908 Z20 E6522.885345 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X169.362114 Y160.194143 Z20 E6532.212211 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X170.101836 Y161.758155 Z20 E6539.405223 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X170.32128 Y162.222129 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=end-early tail
G1 X171.474605 Y164.146336 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=end-early tail
G1 X172.810981 Y165.94823 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0011
G0 X172.810981 Y165.94823 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0012 note=intra-page lift
G0 X202.642344 Y158.081908 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0012 note=intra-page XY
G0 X202.642344 Y158.081908 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0012 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0012
G1 X203.147679 Y159.494224 Z20 E6539.717037 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X203.398114 Y160.194143 Z20 E6540.102678 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X203.721613 Y160.878125 Z20 E6540.652478 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X204.35728 Y162.222129 Z20 E6542.195043 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X204.364093 Y162.233496 Z20 E6542.211547 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X205.135247 Y163.520089 Z20 E6544.394244 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X205.510605 Y164.146336 Z20 E6545.682318 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X205.96922 Y164.764707 Z20 E6547.200567 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X206.846981 Y165.94823 Z20 E6550.564502 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X206.86478 Y165.967868 Z20 E6550.630519 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X207.872118 Y167.079295 Z20 E6554.684098 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X208.353539 Y167.610461 Z20 E6556.841597 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X208.9338 Y168.136379 Z20 E6559.361304 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X210.01577 Y169.117019 Z20 E6564.513601 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X210.047702 Y169.140701 Z20 E6564.662138 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X211.252513 Y170.03425 Z20 E6570.5866 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X211.817664 Y170.453395 Z20 E6573.511906 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X213.741871 Y171.60672 Z20 E6582.838771 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X215.769857 Y172.565886 Z20 E6592.165637 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X217.882092 Y173.321656 Z20 E6601.492502 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X220.058235 Y173.866752 Z20 E6610.819368 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X222.277328 Y174.195923 Z20 E6620.146233 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X224.518 Y174.306 Z20 E6629.473099 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X226.758672 Y174.195923 Z20 E6638.799965 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X228.977765 Y173.866752 Z20 E6648.12683 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X231.153908 Y173.321656 Z20 E6657.453696 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X233.266143 Y172.565886 Z20 E6666.780561 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X235.294129 Y171.60672 Z20 E6676.107427 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X237.218336 Y170.453395 Z20 E6685.434292 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X239.02023 Y169.117019 Z20 E6694.761158 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X240.682461 Y167.610461 Z20 E6704.088024 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X242.189019 Y165.94823 Z20 E6713.414889 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X243.525395 Y164.146336 Z20 E6722.741755 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X244.67872 Y162.222129 Z20 E6732.06862 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X245.637886 Y160.194143 Z20 E6741.395486 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X246.393656 Y158.081908 Z20 E6750.722351 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X246.938752 Y155.905765 Z20 E6760.049217 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X247.267923 Y153.686672 Z20 E6769.376083 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X247.378 Y151.446 Z20 E6778.702948 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X247.267923 Y149.205328 Z20 E6788.029814 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X246.938752 Y146.986235 Z20 E6797.356679 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X246.393656 Y144.810092 Z20 E6806.683545 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X245.637886 Y142.697857 Z20 E6816.01041 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X244.67872 Y140.669871 Z20 E6825.337276 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X243.525395 Y138.745664 Z20 E6834.664142 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X242.189019 Y136.94377 Z20 E6843.991007 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X240.682461 Y135.281539 Z20 E6853.317873 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X239.02023 Y133.774981 Z20 E6862.644738 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X237.218336 Y132.438605 Z20 E6871.971604 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X235.294129 Y131.28528 Z20 E6881.298469 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X233.266143 Y130.326114 Z20 E6890.625335 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X231.153908 Y129.570344 Z20 E6899.952201 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X228.977765 Y129.025248 Z20 E6909.279066 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X226.758672 Y128.696077 Z20 E6918.605932 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X224.518 Y128.586 Z20 E6927.932797 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X222.277328 Y128.696077 Z20 E6937.259663 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X220.058235 Y129.025248 Z20 E6946.586528 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X217.882092 Y129.570344 Z20 E6955.913394 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X215.769857 Y130.326114 Z20 E6965.240259 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X213.741871 Y131.28528 Z20 E6974.567125 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X211.817664 Y132.438605 Z20 E6983.893991 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X210.01577 Y133.774981 Z20 E6993.220856 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X208.353539 Y135.281539 Z20 E7002.547722 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X206.846981 Y136.94377 Z20 E7011.874587 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X205.510605 Y138.745664 Z20 E7021.201453 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X204.35728 Y140.669871 Z20 E7030.528318 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X203.398114 Y142.697857 Z20 E7039.855184 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X202.642344 Y144.810092 Z20 E7049.18205 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X202.097248 Y146.986235 Z20 E7058.508915 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X201.768077 Y149.205328 Z20 E7067.835781 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X201.658 Y151.446 Z20 E7077.162646 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X201.742893 Y153.174038 Z20 E7084.355659 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X201.768077 Y153.686672 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
G1 X202.097248 Y155.905765 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
G1 X202.642344 Y158.081908 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0012
G0 X202.642344 Y158.081908 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0013 note=intra-page lift
G0 X210.01577 Y167.810981 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0013 note=intra-page XY
G0 X210.01577 Y167.810981 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0013 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0013
G1 X208.904343 Y168.818319 Z20 E7084.667472 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X208.353539 Y169.317539 Z20 E7085.053114 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X207.84542 Y169.878162 Z20 E7085.602914 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X206.846981 Y170.97977 Z20 E7087.145478 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X206.839087 Y170.990414 Z20 E7087.161982 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X205.945538 Y172.195225 Z20 E7089.344679 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X205.510605 Y172.781664 Z20 E7090.632753 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X205.114808 Y173.442011 Z20 E7092.151003 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X204.35728 Y174.705871 Z20 E7095.514938 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X204.345948 Y174.72983 Z20 E7095.580954 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X203.704615 Y176.085814 Z20 E7099.634533 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X203.398114 Y176.733857 Z20 E7101.792032 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X203.134285 Y177.471208 Z20 E7104.31174 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X202.642344 Y178.846092 Z20 E7109.464037 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X202.632684 Y178.884656 Z20 E7109.612574 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X202.268214 Y180.339703 Z20 E7115.537035 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X202.097248 Y181.022235 Z20 E7118.462341 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X201.768077 Y183.241328 Z20 E7127.789206 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X201.658 Y185.482 Z20 E7137.116072 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X201.768077 Y187.722672 Z20 E7146.442938 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X202.097248 Y189.941765 Z20 E7155.769803 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X202.642344 Y192.117908 Z20 E7165.096669 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X203.398114 Y194.230143 Z20 E7174.423534 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X204.35728 Y196.258129 Z20 E7183.7504 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X205.510605 Y198.182336 Z20 E7193.077265 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X206.846981 Y199.98423 Z20 E7202.404131 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X208.353539 Y201.646461 Z20 E7211.730997 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X210.01577 Y203.153019 Z20 E7221.057862 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X211.817664 Y204.489395 Z20 E7230.384728 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X213.741871 Y205.64272 Z20 E7239.711593 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X215.769857 Y206.601886 Z20 E7249.038459 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X217.882092 Y207.357656 Z20 E7258.365324 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X220.058235 Y207.902752 Z20 E7267.69219 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X222.277328 Y208.231923 Z20 E7277.019056 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X224.518 Y208.342 Z20 E7286.345921 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X226.758672 Y208.231923 Z20 E7295.672787 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X228.977765 Y207.902752 Z20 E7304.999652 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X231.153908 Y207.357656 Z20 E7314.326518 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X233.266143 Y206.601886 Z20 E7323.653383 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X235.294129 Y205.64272 Z20 E7332.980249 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X237.218336 Y204.489395 Z20 E7342.307115 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X239.02023 Y203.153019 Z20 E7351.63398 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X240.682461 Y201.646461 Z20 E7360.960846 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X242.189019 Y199.98423 Z20 E7370.287711 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X243.525395 Y198.182336 Z20 E7379.614577 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X244.67872 Y196.258129 Z20 E7388.941442 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X245.637886 Y194.230143 Z20 E7398.268308 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X246.393656 Y192.117908 Z20 E7407.595174 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X246.938752 Y189.941765 Z20 E7416.922039 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X247.267923 Y187.722672 Z20 E7426.248905 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X247.378 Y185.482 Z20 E7435.57577 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X247.267923 Y183.241328 Z20 E7444.902636 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X246.938752 Y181.022235 Z20 E7454.229501 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X246.393656 Y178.846092 Z20 E7463.556367 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X245.637886 Y176.733857 Z20 E7472.883232 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X244.67872 Y174.705871 Z20 E7482.210098 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X243.525395 Y172.781664 Z20 E7491.536964 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X242.189019 Y170.97977 Z20 E7500.863829 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X240.682461 Y169.317539 Z20 E7510.190695 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X239.02023 Y167.810981 Z20 E7519.51756 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X237.218336 Y166.474605 Z20 E7528.844426 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X235.294129 Y165.32128 Z20 E7538.171291 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X233.266143 Y164.362114 Z20 E7547.498157 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X231.153908 Y163.606344 Z20 E7556.825023 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X228.977765 Y163.061248 Z20 E7566.151888 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X226.758672 Y162.732077 Z20 E7575.478754 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X224.518 Y162.622 Z20 E7584.805619 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X222.277328 Y162.732077 Z20 E7594.132485 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X220.058235 Y163.061248 Z20 E7603.45935 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X217.882092 Y163.606344 Z20 E7612.786216 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X215.769857 Y164.362114 Z20 E7622.113082 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X214.205845 Y165.101836 Z20 E7629.306094 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X213.741871 Y165.32128 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
G1 X211.817664 Y166.474605 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
G1 X210.01577 Y167.810981 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0013
G0 X210.01577 Y167.810981 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0014 note=intra-page lift
G0 X236.73831 Y158.249503 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0014 note=intra-page XY
G0 X236.73831 Y158.249503 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0014 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0014
G1 X237.243645 Y159.661819 Z20 E7629.617908 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X237.434114 Y160.194143 Z20 E7629.897261 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X237.833718 Y161.039036 Z20 E7630.553349 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X238.39328 Y162.222129 Z20 E7631.878946 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X238.491603 Y162.386172 Z20 E7632.112418 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X239.262757 Y163.672765 Z20 E7634.295114 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X239.546605 Y164.146336 Z20 E7635.255542 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X240.111255 Y164.907678 Z20 E7637.101438 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X240.882981 Y165.94823 Z20 E7640.027048 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X241.020318 Y166.099758 Z20 E7640.531389 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X242.027656 Y167.211185 Z20 E7644.584968 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X242.389539 Y167.610461 Z20 E7646.193463 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X243.101689 Y168.255917 Z20 E7649.262175 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X244.05177 Y169.117019 Z20 E7653.754788 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X244.226673 Y169.246736 Z20 E7654.563009 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X245.431484 Y170.140285 Z20 E7660.48747 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X245.853664 Y170.453395 Z20 E7662.672736 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X247.777871 Y171.60672 Z20 E7671.999602 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X249.805857 Y172.565886 Z20 E7681.326467 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X251.918092 Y173.321656 Z20 E7690.653333 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X254.094235 Y173.866752 Z20 E7699.980199 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X256.313328 Y174.195923 Z20 E7709.307064 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X258.554 Y174.306 Z20 E7718.63393 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X260.794672 Y174.195923 Z20 E7727.960795 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X263.013765 Y173.866752 Z20 E7737.287661 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X265.189908 Y173.321656 Z20 E7746.614526 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X267.302143 Y172.565886 Z20 E7755.941392 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X269.330129 Y171.60672 Z20 E7765.268258 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X271.254336 Y170.453395 Z20 E7774.595123 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X273.05623 Y169.117019 Z20 E7783.921989 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X274.718461 Y167.610461 Z20 E7793.248854 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X276.225019 Y165.94823 Z20 E7802.57572 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X277.561395 Y164.146336 Z20 E7811.902585 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X278.71472 Y162.222129 Z20 E7821.229451 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X279.673886 Y160.194143 Z20 E7830.556317 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X280.429656 Y158.081908 Z20 E7839.883182 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X280.974752 Y155.905765 Z20 E7849.210048 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X281.303923 Y153.686672 Z20 E7858.536913 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X281.414 Y151.446 Z20 E7867.863779 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X281.303923 Y149.205328 Z20 E7877.190644 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X280.974752 Y146.986235 Z20 E7886.51751 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X280.429656 Y144.810092 Z20 E7895.844375 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X279.673886 Y142.697857 Z20 E7905.171241 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X278.71472 Y140.669871 Z20 E7914.498107 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X277.561395 Y138.745664 Z20 E7923.824972 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X276.225019 Y136.94377 Z20 E7933.151838 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X274.718461 Y135.281539 Z20 E7942.478703 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X273.05623 Y133.774981 Z20 E7951.805569 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X271.254336 Y132.438605 Z20 E7961.132434 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X269.330129 Y131.28528 Z20 E7970.4593 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X267.302143 Y130.326114 Z20 E7979.786166 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X265.189908 Y129.570344 Z20 E7989.113031 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X263.013765 Y129.025248 Z20 E7998.439897 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X260.794672 Y128.696077 Z20 E8007.766762 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X258.554 Y128.586 Z20 E8017.093628 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X256.313328 Y128.696077 Z20 E8026.420493 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X254.094235 Y129.025248 Z20 E8035.747359 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X251.918092 Y129.570344 Z20 E8045.074225 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X249.805857 Y130.326114 Z20 E8054.40109 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X247.777871 Y131.28528 Z20 E8063.727956 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X245.853664 Y132.438605 Z20 E8073.054821 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X244.05177 Y133.774981 Z20 E8082.381687 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X242.389539 Y135.281539 Z20 E8091.708552 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X240.882981 Y136.94377 Z20 E8101.035418 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X239.546605 Y138.745664 Z20 E8110.362284 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X238.39328 Y140.669871 Z20 E8119.689149 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X237.434114 Y142.697857 Z20 E8129.016015 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X236.678344 Y144.810092 Z20 E8138.34288 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X236.133248 Y146.986235 Z20 E8147.669746 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X235.804077 Y149.205328 Z20 E8156.996611 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X235.694 Y151.446 Z20 E8166.323477 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X235.787627 Y153.351824 Z20 E8174.256529 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X235.804077 Y153.686672 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X236.133248 Y155.905765 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X236.678344 Y158.081908 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X236.73831 Y158.249503 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0014
G0 X236.73831 Y158.249503 Z24 F7200 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0015 note=intra-page lift
G0 X244.05177 Y167.810981 Z24 F7200 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0015 note=intra-page XY
G0 X244.05177 Y167.810981 Z20 F7200 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0015 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0015
G1 X242.940343 Y168.818319 Z20 E8174.568343 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X242.389539 Y169.317539 Z20 E8174.953984 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X241.88142 Y169.878162 Z20 E8175.503784 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X240.882981 Y170.97977 Z20 E8177.046349 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X240.875087 Y170.990414 Z20 E8177.062853 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X239.981538 Y172.195225 Z20 E8179.245549 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X239.546605 Y172.781664 Z20 E8180.533624 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X239.150808 Y173.442011 Z20 E8182.051873 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X238.39328 Y174.705871 Z20 E8185.415808 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X238.381948 Y174.72983 Z20 E8185.481825 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X237.740615 Y176.085814 Z20 E8189.535404 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X237.434114 Y176.733857 Z20 E8191.692903 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X237.170285 Y177.471208 Z20 E8194.21261 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X236.678344 Y178.846092 Z20 E8199.364907 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X236.668684 Y178.884656 Z20 E8199.513444 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X236.304214 Y180.339703 Z20 E8205.437906 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X236.133248 Y181.022235 Z20 E8208.363211 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X235.804077 Y183.241328 Z20 E8217.690077 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X235.694 Y185.482 Z20 E8227.016943 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X235.804077 Y187.722672 Z20 E8236.343808 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X236.133248 Y189.941765 Z20 E8245.670674 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X236.678344 Y192.117908 Z20 E8254.997539 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X237.434114 Y194.230143 Z20 E8264.324405 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X238.39328 Y196.258129 Z20 E8273.65127 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X239.546605 Y198.182336 Z20 E8282.978136 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X240.882981 Y199.98423 Z20 E8292.305002 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X242.389539 Y201.646461 Z20 E8301.631867 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X244.05177 Y203.153019 Z20 E8310.958733 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X245.853664 Y204.489395 Z20 E8320.285598 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X247.777871 Y205.64272 Z20 E8329.612464 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X249.805857 Y206.601886 Z20 E8338.939329 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X251.918092 Y207.357656 Z20 E8348.266195 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X254.094235 Y207.902752 Z20 E8357.593061 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X256.313328 Y208.231923 Z20 E8366.919926 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X258.554 Y208.342 Z20 E8376.246792 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X260.794672 Y208.231923 Z20 E8385.573657 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X263.013765 Y207.902752 Z20 E8394.900523 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X265.189908 Y207.357656 Z20 E8404.227388 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X267.302143 Y206.601886 Z20 E8413.554254 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X269.330129 Y205.64272 Z20 E8422.88112 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X271.254336 Y204.489395 Z20 E8432.207985 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X273.05623 Y203.153019 Z20 E8441.534851 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X274.718461 Y201.646461 Z20 E8450.861716 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X276.225019 Y199.98423 Z20 E8460.188582 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X277.561395 Y198.182336 Z20 E8469.515447 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X278.71472 Y196.258129 Z20 E8478.842313 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X279.673886 Y194.230143 Z20 E8488.169178 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X280.429656 Y192.117908 Z20 E8497.496044 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X280.974752 Y189.941765 Z20 E8506.82291 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X281.303923 Y187.722672 Z20 E8516.149775 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X281.414 Y185.482 Z20 E8525.476641 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X281.303923 Y183.241328 Z20 E8534.803506 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X280.974752 Y181.022235 Z20 E8544.130372 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X280.429656 Y178.846092 Z20 E8553.457237 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X279.673886 Y176.733857 Z20 E8562.784103 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X278.71472 Y174.705871 Z20 E8572.110969 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X277.561395 Y172.781664 Z20 E8581.437834 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X276.225019 Y170.97977 Z20 E8590.7647 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X274.718461 Y169.317539 Z20 E8600.091565 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X273.05623 Y167.810981 Z20 E8609.418431 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X271.254336 Y166.474605 Z20 E8618.745296 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X269.330129 Y165.32128 Z20 E8628.072162 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X267.302143 Y164.362114 Z20 E8637.399028 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X265.189908 Y163.606344 Z20 E8646.725893 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X263.013765 Y163.061248 Z20 E8656.052759 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X260.794672 Y162.732077 Z20 E8665.379624 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X258.554 Y162.622 Z20 E8674.70649 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X256.313328 Y162.732077 Z20 E8684.033355 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X254.094235 Y163.061248 Z20 E8693.360221 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X251.918092 Y163.606344 Z20 E8702.687087 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X249.805857 Y164.362114 Z20 E8712.013952 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X248.241845 Y165.101836 Z20 E8719.206964 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X247.777871 Y165.32128 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=end-early tail
G1 X245.853664 Y166.474605 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=end-early tail
G1 X244.05177 Y167.810981 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0015
; CLAYLINE_PAGE index=1
G0 X244.05177 Y167.810981 Z70 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0000 note=inter-page clearance above completed material
G0 X143.945 Y266.055 Z70 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0000 note=inter-page XY within common stack footprint
G0 X143.945 Y266.055 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0000 note=inter-page approach
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-padma-gate page_name=padma-gate z_mode=drape
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X145.090206 Y267.023764 Z22 E8719.518778 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X145.321 Y267.219 Z22 E8719.657123 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X146.347794 Y267.835594 Z22 E8720.454219 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X146.908 Y268.172 Z22 E8721.056742 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.690964 Y268.493885 Z22 E8722.013288 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X148.708 Y268.912 Z22 E8723.552378 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X149.09514 Y269.014082 Z22 E8724.195985 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X150.545564 Y269.396532 Z22 E8727.002309 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X150.718 Y269.442 Z22 E8727.377419 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X152.026434 Y269.628583 Z22 E8730.43226 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X152.941 Y269.759 Z22 E8732.855006 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X153.516637 Y269.784069 Z22 E8734.485839 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X155.015216 Y269.849332 Z22 E8739.163045 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X155.375 Y269.865 Z22 E8740.378798 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X156.514875 Y269.865 Z22 E8744.463879 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X158.014875 Y269.865 Z22 E8750.388341 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=prime ramp
G1 X259.599 Y269.865 Z22 E9172.726055 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X262.033 Y269.759 Z22 E9182.855042 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X264.256 Y269.442 Z22 E9192.190698 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X266.266 Y268.912 Z22 E9200.832935 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X268.066 Y268.172 Z22 E9208.924193 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X269.653 Y267.219 Z22 E9216.620405 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X271.029 Y266.055 Z22 E9224.113482 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X272.193 Y264.679 Z22 E9231.60656 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X273.146 Y263.092 Z22 E9239.302771 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X273.886 Y261.292 Z22 E9247.39403 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X274.416 Y259.282 Z22 E9256.036267 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X274.733 Y257.059 Z22 E9265.371922 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X274.839 Y254.625 Z22 E9275.50091 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X274.839 Y150.401 Z22 E9708.813949 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X274.733 Y147.967 Z22 E9718.942937 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X274.416 Y145.744 Z22 E9728.278593 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X273.886 Y143.734 Z22 E9736.92083 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X273.146 Y141.934 Z22 E9745.012088 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X272.193 Y140.347 Z22 E9752.7083 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X271.029 Y138.971 Z22 E9760.201377 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X269.653 Y137.807 Z22 E9767.694454 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X268.066 Y136.854 Z22 E9775.390666 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X266.266 Y136.114 Z22 E9783.481925 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X264.256 Y135.584 Z22 E9792.124161 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X262.033 Y135.267 Z22 E9801.459817 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X259.599 Y135.161 Z22 E9811.588805 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X155.375 Y135.161 Z22 E10244.901844 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.941 Y135.267 Z22 E10255.030832 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.718 Y135.584 Z22 E10264.366488 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X148.708 Y136.114 Z22 E10273.008724 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X146.908 Y136.854 Z22 E10281.099983 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.321 Y137.807 Z22 E10288.796194 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X143.945 Y138.971 Z22 E10296.289272 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.781 Y140.347 Z22 E10303.782349 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X141.828 Y141.934 Z22 E10311.478561 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X141.088 Y143.734 Z22 E10319.569819 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.558 Y145.744 Z22 E10328.212056 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.241 Y147.967 Z22 E10337.547712 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.135 Y150.401 Z22 E10347.676699 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.135 Y254.625 Z22 E10780.989739 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.241 Y257.059 Z22 E10791.118726 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.558 Y259.282 Z22 E10800.454382 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X141.088 Y261.292 Z22 E10809.096619 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X141.315998 Y261.84659 Z22 E10811.589582 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X141.828 Y263.092 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=end-early tail
G1 X142.781 Y264.679 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=end-early tail
G1 X143.945 Y266.055 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
G0 X143.945 Y266.055 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0001 note=intra-page lift
G0 X164.382 Y245.618 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0001 note=intra-page XY
G0 X164.382 Y245.618 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X165.233 Y246.354 Z22 E10811.765015 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X165.553884 Y246.547825 Z22 E10811.901396 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X166.175 Y246.923 Z22 E10812.276049 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X166.904223 Y247.183537 Z22 E10812.836837 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X167.219 Y247.296 Z22 E10813.130263 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X167.782 Y247.399 Z22 E10813.704593 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X168.375294 Y247.409769 Z22 E10814.395906 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X168.994 Y247.421 Z22 E10815.220784 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X169.647 Y247.332 Z22 E10816.215997 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X169.860762 Y247.271513 Z22 E10816.578602 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X171.05 Y246.935 Z22 E10818.845657 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X171.293496 Y246.832816 Z22 E10819.384926 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X171.803 Y246.619 Z22 E10820.575856 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X172.633973 Y246.16387 Z22 E10822.814878 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X173.417 Y245.735 Z22 E10825.152391 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X173.921966 Y245.397772 Z22 E10826.868456 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X174.281 Y245.158 Z22 E10828.150752 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X175.123475 Y244.501171 Z22 E10831.545663 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X176.128 Y243.718 Z22 E10836.006999 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X176.294671 Y243.56499 Z22 E10836.846497 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X177.39965 Y242.550584 Z22 E10842.770959 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=prime ramp
G1 X178.141 Y241.87 Z22 E10846.954986 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X180.331 Y239.583 Z22 E10860.119597 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X182.136 Y238.058 Z22 E10869.943704 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X183.749 Y236.503 Z22 E10879.258578 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X186.619 Y233.417 Z22 E10896.779587 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X188.739 Y230.886 Z22 E10910.505918 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X192.062 Y226.431 Z22 E10933.612645 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X194.28 Y223.053 Z22 E10950.413545 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X196.422 Y219.372 Z22 E10968.119845 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X198.424 Y215.408 Z22 E10986.582825 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X200.22 Y211.183 Z22 E11005.669514 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X201.021 Y208.979 Z22 E11015.419061 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X198.817 Y209.78 Z22 E11025.168608 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X194.592 Y211.576 Z22 E11044.255298 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X190.628 Y213.578 Z22 E11062.718277 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X186.947 Y215.72 Z22 E11080.424577 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X183.569 Y217.938 Z22 E11097.225477 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X179.114 Y221.261 Z22 E11120.332204 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X176.583 Y223.381 Z22 E11134.058535 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X173.497 Y226.251 Z22 E11151.579544 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X171.942 Y227.864 Z22 E11160.894418 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X170.417 Y229.669 Z22 E11170.718526 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X168.13 Y231.859 Z22 E11183.883137 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X166.282 Y233.872 Z22 E11195.244097 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X164.842 Y235.719 Z22 E11204.981041 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X164.265 Y236.583 Z22 E11209.300509 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X163.381 Y238.197 Z22 E11216.951303 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X163.065 Y238.95 Z22 E11220.346406 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X162.668 Y240.353 Z22 E11226.408428 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X162.579 Y241.006 Z22 E11229.148386 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X162.581156 Y241.124789 Z22 E11229.642333 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X162.601 Y242.218 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=end-early tail
G1 X162.704 Y242.781 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=end-early tail
G1 X163.077 Y243.825 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=end-early tail
G1 X163.646 Y244.767 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=end-early tail
G1 X164.382 Y245.618 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
G0 X164.382 Y245.618 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0002 note=intra-page lift
G0 X166.537032 Y243.462968 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0002 note=intra-page XY
G0 X166.537032 Y243.462968 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0002
G1 X167.623403 Y244.497279 Z22 E11229.954146 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X168.595678 Y245.422962 Z22 E11230.762035 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X168.714966 Y245.52586 Z22 E11230.889588 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X169.850779 Y246.50562 Z22 E11232.448657 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X170.748016 Y247.279581 Z22 E11234.121141 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X170.996403 Y247.473425 Z22 E11234.631353 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X172.178923 Y248.396272 Z22 E11237.437677 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X172.988862 Y249.028355 Z22 E11239.719651 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X173.375261 Y249.300487 Z22 E11240.867628 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X174.601638 Y250.1642 Z22 E11244.921207 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X175.312817 Y250.665068 Z22 E11247.557566 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X175.845199 Y251.002195 Z22 E11249.598414 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X177.112479 Y251.804692 Z22 E11254.899248 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X177.714282 Y252.185779 Z22 E11257.634885 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X178.399635 Y252.574027 Z22 E11260.823709 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=prime ramp
G1 X180.187472 Y253.586824 Z22 E11269.36649 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X182.726429 Y254.864828 Z22 E11281.184079 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X185.325037 Y256.016711 Z22 E11293.001668 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X187.977035 Y257.0397 Z22 E11304.819257 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X190.676034 Y257.931329 Z22 E11316.636846 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X193.415532 Y258.68945 Z22 E11328.454435 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X196.188929 Y259.312237 Z22 E11340.272024 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X198.989545 Y259.79819 Z22 E11352.089612 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X201.810631 Y260.146138 Z22 E11363.907201 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X204.645393 Y260.355242 Z22 E11375.72479 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X207.487 Y260.425 Z22 E11387.542379 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X210.328607 Y260.355242 Z22 E11399.359968 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X213.163369 Y260.146138 Z22 E11411.177557 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X215.984455 Y259.79819 Z22 E11422.995146 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X218.785071 Y259.312237 Z22 E11434.812735 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X221.558468 Y258.68945 Z22 E11446.630324 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X224.297966 Y257.931329 Z22 E11458.447913 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X226.996965 Y257.0397 Z22 E11470.265502 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X229.648963 Y256.016711 Z22 E11482.083091 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X232.247571 Y254.864828 Z22 E11493.90068 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X234.786528 Y253.586824 Z22 E11505.718269 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X237.259718 Y252.185779 Z22 E11517.535858 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X239.661183 Y250.665068 Z22 E11529.353447 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X241.985138 Y249.028355 Z22 E11541.171036 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X244.225984 Y247.279581 Z22 E11552.988625 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X246.378322 Y245.422962 Z22 E11564.806214 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X248.436968 Y243.462968 Z22 E11576.623803 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X250.396962 Y241.404322 Z22 E11588.441392 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X252.253581 Y239.251984 Z22 E11600.258981 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X254.002355 Y237.011138 Z22 E11612.076569 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X255.639068 Y234.687183 Z22 E11623.894158 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X257.159779 Y232.285718 Z22 E11635.711747 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X258.560824 Y229.812528 Z22 E11647.529336 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X259.838828 Y227.273571 Z22 E11659.346925 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X260.990711 Y224.674963 Z22 E11671.164514 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X262.0137 Y222.022965 Z22 E11682.982103 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X262.905329 Y219.323966 Z22 E11694.799692 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X263.66345 Y216.584468 Z22 E11706.617281 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X264.286237 Y213.811071 Z22 E11718.43487 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X264.77219 Y211.010455 Z22 E11730.252459 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X265.120138 Y208.189369 Z22 E11742.070048 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X265.329242 Y205.354607 Z22 E11753.887637 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X265.399 Y202.513 Z22 E11765.705226 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X265.329242 Y199.671393 Z22 E11777.522815 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X265.120138 Y196.836631 Z22 E11789.340404 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X264.77219 Y194.015545 Z22 E11801.157993 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X264.286237 Y191.214929 Z22 E11812.975582 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X263.66345 Y188.441532 Z22 E11824.793171 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X262.905329 Y185.702034 Z22 E11836.61076 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X262.0137 Y183.003035 Z22 E11848.428349 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X260.990711 Y180.351037 Z22 E11860.245938 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X259.838828 Y177.752429 Z22 E11872.063527 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X258.560824 Y175.213472 Z22 E11883.881115 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X257.159779 Y172.740282 Z22 E11895.698704 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X255.639068 Y170.338817 Z22 E11907.516293 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X254.002355 Y168.014862 Z22 E11919.333882 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X252.253581 Y165.774016 Z22 E11931.151471 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X250.396962 Y163.621678 Z22 E11942.96906 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X248.436968 Y161.563032 Z22 E11954.786649 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X246.378322 Y159.603038 Z22 E11966.604238 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X244.225984 Y157.746419 Z22 E11978.421827 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X241.985138 Y155.997645 Z22 E11990.239416 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X239.661183 Y154.360932 Z22 E12002.057005 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X237.259718 Y152.840221 Z22 E12013.874594 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X234.786528 Y151.439176 Z22 E12025.692183 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X232.247571 Y150.161172 Z22 E12037.509772 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X229.648963 Y149.009289 Z22 E12049.327361 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X226.996965 Y147.9863 Z22 E12061.14495 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X224.297966 Y147.094671 Z22 E12072.962539 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X221.558468 Y146.33655 Z22 E12084.780128 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X218.785071 Y145.713763 Z22 E12096.597717 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X215.984455 Y145.22781 Z22 E12108.415306 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X213.163369 Y144.879862 Z22 E12120.232895 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X210.328607 Y144.670758 Z22 E12132.050484 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X207.487 Y144.601 Z22 E12143.868072 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X204.645393 Y144.670758 Z22 E12155.685661 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X201.810631 Y144.879862 Z22 E12167.50325 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X198.989545 Y145.22781 Z22 E12179.320839 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X196.188929 Y145.713763 Z22 E12191.138428 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X193.415532 Y146.33655 Z22 E12202.956017 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X190.676034 Y147.094671 Z22 E12214.773606 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X187.977035 Y147.9863 Z22 E12226.591195 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X185.325037 Y149.009289 Z22 E12238.408784 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X182.726429 Y150.161172 Z22 E12250.226373 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X180.187472 Y151.439176 Z22 E12262.043962 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X177.714282 Y152.840221 Z22 E12273.861551 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X175.312817 Y154.360932 Z22 E12285.67914 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X172.988862 Y155.997645 Z22 E12297.496729 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X170.748016 Y157.746419 Z22 E12309.314318 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X168.595678 Y159.603038 Z22 E12321.131907 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X166.537032 Y161.563032 Z22 E12332.949496 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X164.577038 Y163.621678 Z22 E12344.767085 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X162.720419 Y165.774016 Z22 E12356.584674 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X160.971645 Y168.014862 Z22 E12368.402263 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X159.334932 Y170.338817 Z22 E12380.219852 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X157.814221 Y172.740282 Z22 E12392.037441 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X156.413176 Y175.213472 Z22 E12403.855029 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X155.135172 Y177.752429 Z22 E12415.672618 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X153.983289 Y180.351037 Z22 E12427.490207 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X152.9603 Y183.003035 Z22 E12439.307796 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X152.068671 Y185.702034 Z22 E12451.125385 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X151.31055 Y188.441532 Z22 E12462.942974 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X150.687763 Y191.214929 Z22 E12474.760563 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X150.20181 Y194.015545 Z22 E12486.578152 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X149.853862 Y196.836631 Z22 E12498.395741 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X149.644758 Y199.671393 Z22 E12510.21333 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X149.575 Y202.513 Z22 E12522.030919 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X149.644758 Y205.354607 Z22 E12533.848508 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X149.853862 Y208.189369 Z22 E12545.666097 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X150.20181 Y211.010455 Z22 E12557.483686 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X150.687763 Y213.811071 Z22 E12569.301275 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X151.31055 Y216.584468 Z22 E12581.118864 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X152.068671 Y219.323966 Z22 E12592.936453 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X152.9603 Y222.022965 Z22 E12604.754042 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X153.983289 Y224.674963 Z22 E12616.571631 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X155.135172 Y227.273571 Z22 E12628.38922 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X156.413176 Y229.812528 Z22 E12640.206809 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X157.814221 Y232.285718 Z22 E12652.024398 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X159.334932 Y234.687183 Z22 E12663.841986 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X160.971645 Y237.011138 Z22 E12675.659575 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X162.720419 Y239.251984 Z22 E12687.477164 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X163.167794 Y239.770616 Z22 E12690.324758 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002
G1 X164.577038 Y241.404322 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=end-early tail
G1 X166.537032 Y243.462968 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0002
G0 X166.537032 Y243.462968 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0003 note=intra-page lift
G0 X165.473474 Y209.653018 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0003 note=intra-page XY
G0 X165.473474 Y209.653018 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0003 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0003
G1 X166.841 Y209.61 Z22 E12690.584184 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X166.972298 Y209.598537 Z22 E12690.636572 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X168.466615 Y209.468081 Z22 E12691.572013 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X169.960931 Y209.337625 Z22 E12693.131082 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X171.455247 Y209.207169 Z22 E12695.313778 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X172.637 Y209.104 Z22 E12697.481529 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X172.947867 Y209.06155 Z22 E12698.120102 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X174.434074 Y208.858601 Z22 E12701.550053 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X175.920282 Y208.655653 Z22 E12705.603632 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X176.921 Y208.519 Z22 E12708.684384 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X177.403167 Y208.431768 Z22 E12710.280839 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X178.879206 Y208.164728 Z22 E12715.581673 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X180.355244 Y207.897688 Z22 E12721.506135 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=prime ramp
G1 X181.459 Y207.698 Z22 E12726.169512 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X186.183 Y206.61 Z22 E12746.323789 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X191.021 Y205.223 Z22 E12767.248127 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X195.906 Y203.506 Z22 E12788.775601 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X198.343 Y202.513 Z22 E12799.716285 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X195.906 Y201.52 Z22 E12810.656969 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X191.021 Y199.803 Z22 E12832.184443 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X186.183 Y198.416 Z22 E12853.108781 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X181.459 Y197.328 Z22 E12873.263057 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X176.921 Y196.507 Z22 E12892.436146 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X172.637 Y195.922 Z22 E12910.412242 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X166.841 Y195.416 Z22 E12934.600864 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X162.009 Y195.264 Z22 E12954.699923 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X159.44 Y195.305 Z22 E12965.381944 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X156.738 Y195.503 Z22 E12976.645675 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X153.107 Y195.434 Z22 E12991.744344 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X149.975 Y195.551 Z22 E13004.77477 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X147.309 Y195.839 Z22 E13015.923196 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X146.141 Y196.042 Z22 E13020.851972 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X144.114 Y196.558 Z22 E13029.548028 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X143.247 Y196.867 Z22 E13033.374683 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X141.787 Y197.578 Z22 E13040.126164 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X141.186 Y197.976 Z22 E13043.123053 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X140.22 Y198.849 Z22 E13048.536269 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X139.847 Y199.321 Z22 E13051.037398 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X139.304 Y200.322 Z22 E13055.77195 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X139.001 Y201.391 Z22 E13060.391417 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X138.907 Y202.513 Z22 E13065.072493 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X139.001 Y203.635 Z22 E13069.753569 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X139.304 Y204.704 Z22 E13074.373036 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X139.847 Y205.705 Z22 E13079.107589 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X140.22 Y206.177 Z22 E13081.608718 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X141.186 Y207.05 Z22 E13087.021934 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X141.787 Y207.448 Z22 E13090.018823 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X143.247 Y208.159 Z22 E13096.770304 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X144.114 Y208.468 Z22 E13100.596959 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X146.141 Y208.984 Z22 E13109.293015 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X147.309 Y209.187 Z22 E13114.221791 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X149.975 Y209.475 Z22 E13125.370217 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X153.107 Y209.592 Z22 E13138.400642 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X156.738 Y209.523 Z22 E13153.499312 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X159.44 Y209.721 Z22 E13164.763043 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X160.475383 Y209.737524 Z22 E13169.068214 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003
G1 X162.009 Y209.762 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=end-early tail
G1 X165.473474 Y209.653018 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0003 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0003
G0 X165.473474 Y209.653018 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0004 note=intra-page lift
G0 X149.108818 Y207.327824 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0004 note=intra-page XY
G0 X149.108818 Y207.327824 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0004 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0004
G1 X149.176 Y206.855 Z22 E13169.099821 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X149.179292 Y205.832579 Z22 E13169.380028 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X149.184122 Y204.332586 Z22 E13170.315469 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X149.188951 Y202.832594 Z22 E13171.874538 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X149.193781 Y201.332602 Z22 E13174.057234 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X149.198611 Y199.83261 Z22 E13176.863558 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X149.202 Y198.78 Z22 E13179.205241 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X149.161841 Y198.334421 Z22 E13180.293509 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X149.097 Y197.615 Z22 E13182.167696 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X148.850617 Y196.877399 Z22 E13184.347088 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X148.779 Y196.663 Z22 E13185.012018 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X148.541 Y196.266 Z22 E13186.417797 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X147.967479 Y195.692479 Z22 E13189.024295 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X147.906 Y195.631 Z22 E13189.314522 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X147.509 Y195.393 Z22 E13190.894896 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X146.607769 Y195.091959 Z22 E13194.325129 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X146.557 Y195.075 Z22 E13194.52581 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X145.392 Y194.97 Z22 E13199.109607 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X145.11525 Y194.970891 Z22 E13200.24959 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=prime ramp
G1 X137.317 Y194.996 Z22 E13232.671115 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X136.259 Y195.208 Z22 E13237.157205 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X135.412 Y195.631 Z22 E13241.09334 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X134.777 Y196.266 Z22 E13244.826896 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X134.539 Y196.663 Z22 E13246.751306 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X134.221 Y197.615 Z22 E13250.924235 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X134.142 Y198.171 Z22 E13253.259031 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X134.142 Y206.855 Z22 E13289.362908 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X134.354 Y207.913 Z22 E13293.848998 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X134.777 Y208.76 Z22 E13297.785132 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X135.068 Y209.104 Z22 E13299.658402 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X135.809 Y209.633 Z22 E13303.443619 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X136.761 Y209.951 Z22 E13307.616549 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X137.317 Y210.03 Z22 E13309.951345 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X145.475526 Y210.03 Z22 E13343.870556 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004
G1 X146.001 Y210.03 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=end-early tail
G1 X147.059 Y209.818 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=end-early tail
G1 X147.906 Y209.395 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=end-early tail
G1 X148.25 Y209.104 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=end-early tail
G1 X148.779 Y208.363 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=end-early tail
G1 X149.097 Y207.411 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=end-early tail
G1 X149.108818 Y207.327824 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0004 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0004
G0 X149.108818 Y207.327824 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0005 note=intra-page lift
G0 X174.658518 Y179.85522 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0005 note=intra-page XY
G0 X174.658518 Y179.85522 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0005 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0005
G1 X175.756922 Y180.876742 Z22 E13344.182369 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X176.583 Y181.645 Z22 E13344.827747 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X176.868096 Y181.8838 Z22 E13345.117811 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X178.018003 Y182.846978 Z22 E13346.676879 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X179.114 Y183.765 Z22 E13348.743311 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X179.17037 Y183.807047 Z22 E13348.859576 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X180.37273 Y184.703891 Z22 E13351.6659 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X181.57509 Y185.600736 Z22 E13355.095851 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X182.77745 Y186.49758 Z22 E13359.14943 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X183.569 Y187.088 Z22 E13362.158439 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X183.99741 Y187.369294 Z22 E13363.826637 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X185.251279 Y188.192587 Z22 E13369.127471 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X186.505149 Y189.01588 Z22 E13375.051932 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=prime ramp
G1 X186.947 Y189.306 Z22 E13377.249533 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X190.628 Y191.448 Z22 E13394.955833 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X194.592 Y193.45 Z22 E13413.418813 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X198.817 Y195.246 Z22 E13432.505502 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X201.021 Y196.047 Z22 E13442.255049 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X200.22 Y193.843 Z22 E13452.004596 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X198.424 Y189.618 Z22 E13471.091285 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X196.422 Y185.654 Z22 E13489.554265 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X194.28 Y181.973 Z22 E13507.260565 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X192.062 Y178.595 Z22 E13524.061465 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X188.739 Y174.14 Z22 E13547.168192 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X186.619 Y171.609 Z22 E13560.894523 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X183.749 Y168.523 Z22 E13578.415532 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X182.136 Y166.968 Z22 E13587.730406 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X180.331 Y165.443 Z22 E13597.554513 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X178.141 Y163.156 Z22 E13610.719124 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X176.128 Y161.308 Z22 E13622.080085 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X174.281 Y159.868 Z22 E13631.817029 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X173.417 Y159.291 Z22 E13636.136497 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X171.803 Y158.407 Z22 E13643.787291 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X171.05 Y158.091 Z22 E13647.182394 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X169.647 Y157.694 Z22 E13653.244416 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X168.994 Y157.605 Z22 E13655.984374 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X167.782 Y157.627 Z22 E13661.024114 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X167.219 Y157.73 Z22 E13663.403645 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X166.175 Y158.103 Z22 E13668.012802 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X165.233 Y158.672 Z22 E13672.588196 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X164.382 Y159.408 Z22 E13677.265905 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X163.646 Y160.259 Z22 E13681.943614 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X163.077 Y161.201 Z22 E13686.519008 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X162.704 Y162.245 Z22 E13691.128164 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X162.601 Y162.808 Z22 E13693.507696 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X162.579 Y164.02 Z22 E13698.547436 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X162.668 Y164.673 Z22 E13701.287394 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X163.065 Y166.076 Z22 E13707.349416 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X163.381 Y166.829 Z22 E13710.744519 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X164.265 Y168.443 Z22 E13718.395313 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X164.842 Y169.307 Z22 E13722.714781 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X166.282 Y171.154 Z22 E13732.451725 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X168.13 Y173.167 Z22 E13743.812685 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X170.417 Y175.357 Z22 E13756.977296 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X171.184771 Y176.265739 Z22 E13761.923306 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005
G1 X171.942 Y177.162 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=end-early tail
G1 X173.497 Y178.775 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=end-early tail
G1 X174.658518 Y179.85522 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0005 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0005
G0 X174.658518 Y179.85522 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0006 note=intra-page lift
G0 X202.016286 Y174.905743 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0006 note=intra-page XY
G0 X202.016286 Y174.905743 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0006 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0006
G1 X202.283326 Y176.381781 Z22 E13762.23512 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X202.302 Y176.485 Z22 E13762.280255 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X202.615114 Y177.844514 Z22 E13763.170561 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X202.951771 Y179.306247 Z22 E13764.72963 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X203.288427 Y180.76798 Z22 E13766.912326 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X203.39 Y181.209 Z22 E13767.693331 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X203.678659 Y182.215873 Z22 E13769.71865 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X204.09204 Y183.657787 Z22 E13773.148602 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X204.50542 Y185.099702 Z22 E13777.202181 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X204.777 Y186.047 Z22 E13780.204708 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X204.94762 Y186.532429 Z22 E13781.879387 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X205.445017 Y187.94756 Z22 E13787.180221 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X205.942413 Y189.362691 Z22 E13793.104683 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=prime ramp
G1 X206.494 Y190.932 Z22 E13800.020394 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X207.487 Y193.369 Z22 E13810.961078 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X208.48 Y190.932 Z22 E13821.901762 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X210.197 Y186.047 Z22 E13843.429236 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X211.584 Y181.209 Z22 E13864.353574 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X212.672 Y176.485 Z22 E13884.507851 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X213.493 Y171.947 Z22 E13903.68094 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X214.078 Y167.663 Z22 E13921.657036 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X214.584 Y161.867 Z22 E13945.845657 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X214.736 Y157.035 Z22 E13965.944716 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X214.695 Y154.466 Z22 E13976.626737 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X214.497 Y151.764 Z22 E13987.890468 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X214.566 Y148.133 Z22 E14002.989138 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X214.449 Y145.001 Z22 E14016.019563 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X214.161 Y142.335 Z22 E14027.167989 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X213.958 Y141.167 Z22 E14032.096765 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X213.442 Y139.14 Z22 E14040.792821 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X213.133 Y138.273 Z22 E14044.619476 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X212.422 Y136.813 Z22 E14051.370957 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X212.024 Y136.212 Z22 E14054.367846 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X211.151 Y135.246 Z22 E14059.781062 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X210.679 Y134.873 Z22 E14062.282192 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X209.678 Y134.33 Z22 E14067.016744 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X208.609 Y134.027 Z22 E14071.636211 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X207.487 Y133.933 Z22 E14076.317287 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X206.365 Y134.027 Z22 E14080.998363 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X205.296 Y134.33 Z22 E14085.61783 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X204.295 Y134.873 Z22 E14090.352382 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X203.823 Y135.246 Z22 E14092.853511 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X202.95 Y136.212 Z22 E14098.266727 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X202.552 Y136.813 Z22 E14101.263616 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X201.841 Y138.273 Z22 E14108.015097 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X201.532 Y139.14 Z22 E14111.841752 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X201.016 Y141.167 Z22 E14120.537808 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X200.813 Y142.335 Z22 E14125.466584 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X200.525 Y145.001 Z22 E14136.61501 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X200.408 Y148.133 Z22 E14149.645436 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X200.477 Y151.764 Z22 E14164.744105 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X200.279 Y154.466 Z22 E14176.007836 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X200.238 Y157.035 Z22 E14186.689857 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X200.39 Y161.867 Z22 E14206.788916 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X200.896 Y167.663 Z22 E14230.977538 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X201.211319 Y169.972102 Z22 E14240.666762 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006
G1 X201.481 Y171.947 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=end-early tail
G1 X202.016286 Y174.905743 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0006 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0006
G0 X202.016286 Y174.905743 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0007 note=intra-page lift
G0 X219.041485 Y184.812827 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0007 note=intra-page XY
G0 X219.041485 Y184.812827 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0007 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0007
G1 X218.552 Y185.654 Z22 E14240.798024 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X218.314523 Y186.124208 Z22 E14240.978576 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X217.638304 Y187.463136 Z22 E14241.914017 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X216.962085 Y188.802064 Z22 E14243.473086 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X216.55 Y189.618 Z22 E14244.728989 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X216.320787 Y190.157211 Z22 E14245.655782 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X215.733973 Y191.537664 Z22 E14248.462106 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X215.147158 Y192.918116 Z22 E14251.892058 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X214.754 Y193.843 Z22 E14254.538957 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X214.584915 Y194.308248 Z22 E14255.945637 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X214.072557 Y195.718031 Z22 E14260.622843 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X213.953 Y196.047 Z22 E14261.803994 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X215.033815 Y195.654199 Z22 E14265.923677 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X216.157 Y195.246 Z22 E14270.593238 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X216.437636 Y195.126705 Z22 E14271.848139 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=prime ramp
G1 X220.382 Y193.45 Z22 E14289.66704 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X224.346 Y191.448 Z22 E14308.13002 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X228.027 Y189.306 Z22 E14325.83632 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X231.405 Y187.088 Z22 E14342.63722 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X235.86 Y183.765 Z22 E14365.743947 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X238.391 Y181.645 Z22 E14379.470277 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X241.477 Y178.775 Z22 E14396.991287 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X243.032 Y177.162 Z22 E14406.30616 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X244.557 Y175.357 Z22 E14416.130268 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X246.844 Y173.167 Z22 E14429.294879 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X248.692 Y171.154 Z22 E14440.655839 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X250.132 Y169.307 Z22 E14450.392784 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X250.709 Y168.443 Z22 E14454.712252 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X251.593 Y166.829 Z22 E14462.363045 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X251.909 Y166.076 Z22 E14465.758149 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X252.306 Y164.673 Z22 E14471.82017 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X252.395 Y164.02 Z22 E14474.560128 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X252.373 Y162.808 Z22 E14479.599869 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X252.27 Y162.245 Z22 E14481.9794 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X251.897 Y161.201 Z22 E14486.588556 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X251.328 Y160.259 Z22 E14491.163951 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X250.592 Y159.408 Z22 E14495.84166 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X249.741 Y158.672 Z22 E14500.519369 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X248.799 Y158.103 Z22 E14505.094763 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X247.755 Y157.73 Z22 E14509.703919 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X247.192 Y157.627 Z22 E14512.08345 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X245.98 Y157.605 Z22 E14517.123191 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X245.327 Y157.694 Z22 E14519.863149 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X243.924 Y158.091 Z22 E14525.925171 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X243.171 Y158.407 Z22 E14529.320274 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X241.557 Y159.291 Z22 E14536.971068 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X240.693 Y159.868 Z22 E14541.290535 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X238.846 Y161.308 Z22 E14551.02748 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X236.833 Y163.156 Z22 E14562.38844 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X234.643 Y165.443 Z22 E14575.553051 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X232.838 Y166.968 Z22 E14585.377159 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X231.225 Y168.523 Z22 E14594.692032 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X228.355 Y171.609 Z22 E14612.213042 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X226.235 Y174.14 Z22 E14625.939373 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X222.912 Y178.595 Z22 E14649.0461 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X221.634948 Y180.539943 Z22 E14658.719513 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007
G1 X220.694 Y181.973 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=end-early tail
G1 X219.041485 Y184.812827 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0007 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0007
G0 X219.041485 Y184.812827 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0008 note=intra-page lift
G0 X212.14379 Y195.543622 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0008 note=intra-page XY
G0 X212.14379 Y195.543622 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0008 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0008
G1 X210.820908 Y194.836527 Z22 E14659.031327 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X210.694653 Y194.769042 Z22 E14659.093686 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X209.396237 Y194.375172 Z22 E14659.966768 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X209.122247 Y194.292058 Z22 E14660.216204 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X207.91441 Y194.173096 Z22 E14661.525837 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X207.487 Y194.131 Z22 E14662.087067 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X206.421633 Y194.23593 Z22 E14663.708533 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X205.851753 Y194.292058 Z22 E14664.706276 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X204.964322 Y194.561257 Z22 E14666.514857 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X204.279347 Y194.769042 Z22 E14668.073831 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X203.587742 Y195.138713 Z22 E14669.944808 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X202.83021 Y195.543622 Z22 E14672.189731 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X202.334677 Y195.950296 Z22 E14673.998387 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X201.560031 Y196.586031 Z22 E14677.053976 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X201.244176 Y196.970901 Z22 E14678.675594 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X200.517622 Y197.85621 Z22 E14682.666567 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X200.350405 Y198.16905 Z22 E14683.976428 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X199.743042 Y199.305347 Z22 E14689.027504 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X199.681627 Y199.507803 Z22 E14689.900889 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=prime ramp
G1 X199.266058 Y200.877753 Z22 E14695.852763 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X199.105 Y202.513 Z22 E14702.684226 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X199.266058 Y204.148247 Z22 E14709.515689 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X199.743042 Y205.720653 Z22 E14716.347151 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X200.517622 Y207.16979 Z22 E14723.178614 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X201.560031 Y208.439969 Z22 E14730.010077 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X202.83021 Y209.482378 Z22 E14736.841539 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X204.279347 Y210.256958 Z22 E14743.673002 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X205.851753 Y210.733942 Z22 E14750.504465 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X207.487 Y210.895 Z22 E14757.335927 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X209.122247 Y210.733942 Z22 E14764.16739 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X210.694653 Y210.256958 Z22 E14770.998853 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X212.14379 Y209.482378 Z22 E14777.830316 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X213.413969 Y208.439969 Z22 E14784.661778 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X214.456378 Y207.16979 Z22 E14791.493241 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X215.230958 Y205.720653 Z22 E14798.324704 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X215.707942 Y204.148247 Z22 E14805.156166 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X215.869 Y202.513 Z22 E14811.987629 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X215.707942 Y200.877753 Z22 E14818.819092 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X215.25143 Y199.372833 Z22 E14825.357358 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008
G1 X215.230958 Y199.305347 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=end-early tail
G1 X214.456378 Y197.85621 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=end-early tail
G1 X213.413969 Y196.586031 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=end-early tail
G1 X212.14379 Y195.543622 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0008 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0008
G0 X212.14379 Y195.543622 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0009 note=intra-page lift
G0 X216.631 Y202.513 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0009 note=intra-page XY
G0 X216.631 Y202.513 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0009 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0009
G1 X218.020109 Y203.079018 Z22 E14825.669172 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X219.068 Y203.506 Z22 E14826.317054 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X219.41561 Y203.628179 Z22 E14826.604613 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X220.830742 Y204.125576 Z22 E14828.163682 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X222.245873 Y204.622972 Z22 E14830.346378 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X223.661004 Y205.120368 Z22 E14833.152702 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X223.953 Y205.223 Z22 E14833.809369 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X225.097392 Y205.551084 Z22 E14836.582654 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X226.539307 Y205.964465 Z22 E14840.636233 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X227.981221 Y206.377845 Z22 E14845.313439 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X228.791 Y206.61 Z22 E14848.213618 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X229.431823 Y206.75759 Z22 E14850.614273 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X230.893556 Y207.094247 Z22 E14856.538735 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=prime ramp
G1 X233.515 Y207.698 Z22 E14867.722754 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X238.053 Y208.519 Z22 E14886.895843 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X242.337 Y209.104 Z22 E14904.871939 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X248.133 Y209.61 Z22 E14929.060561 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X252.965 Y209.762 Z22 E14949.159619 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X255.534 Y209.721 Z22 E14959.84164 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X258.236 Y209.523 Z22 E14971.105372 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X261.867 Y209.592 Z22 E14986.204041 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X264.999 Y209.475 Z22 E14999.234466 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X267.665 Y209.187 Z22 E15010.382893 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X268.833 Y208.984 Z22 E15015.311669 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X270.86 Y208.468 Z22 E15024.007724 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X271.727 Y208.159 Z22 E15027.834379 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X273.187 Y207.448 Z22 E15034.58586 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X273.788 Y207.05 Z22 E15037.582749 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X274.754 Y206.177 Z22 E15042.995966 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X275.127 Y205.705 Z22 E15045.497095 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X275.67 Y204.704 Z22 E15050.231647 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X275.973 Y203.635 Z22 E15054.851114 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X276.067 Y202.513 Z22 E15059.53219 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X275.973 Y201.391 Z22 E15064.213266 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X275.67 Y200.322 Z22 E15068.832733 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X275.127 Y199.321 Z22 E15073.567285 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X274.754 Y198.849 Z22 E15076.068414 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X273.788 Y197.976 Z22 E15081.481631 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X273.187 Y197.578 Z22 E15084.47852 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X271.727 Y196.867 Z22 E15091.230001 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X270.86 Y196.558 Z22 E15095.056656 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X268.833 Y196.042 Z22 E15103.752711 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X267.665 Y195.839 Z22 E15108.681487 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X264.999 Y195.551 Z22 E15119.829914 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X261.867 Y195.434 Z22 E15132.860339 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X258.236 Y195.503 Z22 E15147.959008 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X255.534 Y195.305 Z22 E15159.22274 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X252.965 Y195.264 Z22 E15169.904761 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X248.133 Y195.416 Z22 E15190.003819 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X242.337 Y195.922 Z22 E15214.192441 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X238.053 Y196.507 Z22 E15232.168537 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X233.515 Y197.328 Z22 E15251.341626 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X228.791 Y198.416 Z22 E15271.495903 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X223.953 Y199.803 Z22 E15292.420241 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X221.302452 Y200.734626 Z22 E15304.100814 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009
G1 X219.068 Y201.52 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=end-early tail
G1 X216.631 Y202.513 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0009 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0009
G0 X216.631 Y202.513 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0010 note=intra-page lift
G0 X214.242786 Y209.084317 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0010 note=intra-page XY
G0 X214.242786 Y209.084317 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0010 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0010
G1 X213.953 Y208.979 Z22 E15304.113989 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X214.360041 Y210.098998 Z22 E15304.412628 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X214.754 Y211.183 Z22 E15305.076497 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X214.889605 Y211.502003 Z22 E15305.348069 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X215.47642 Y212.882456 Z22 E15306.907138 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X216.063234 Y214.262908 Z22 E15309.089834 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X216.55 Y215.408 Z22 E15311.373595 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X216.665292 Y215.636281 Z22 E15311.896158 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X217.341511 Y216.975208 Z22 E15315.32611 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X218.017731 Y218.314136 Z22 E15319.379689 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X218.552 Y219.372 Z22 E15323.023355 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X218.710367 Y219.644152 Z22 E15324.056895 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X219.464793 Y220.940624 Z22 E15329.357729 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X220.21922 Y222.237096 Z22 E15335.282191 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=prime ramp
G1 X220.694 Y223.053 Z22 E15339.20684 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X222.912 Y226.431 Z22 E15356.00774 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X226.235 Y230.886 Z22 E15379.114467 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X228.355 Y233.417 Z22 E15392.840798 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X231.225 Y236.503 Z22 E15410.361807 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X232.838 Y238.058 Z22 E15419.676681 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X234.643 Y239.583 Z22 E15429.500788 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X236.833 Y241.87 Z22 E15442.665399 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X238.846 Y243.718 Z22 E15454.026359 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X240.693 Y245.158 Z22 E15463.763304 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X241.557 Y245.735 Z22 E15468.082772 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X243.171 Y246.619 Z22 E15475.733565 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X243.924 Y246.935 Z22 E15479.128669 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X245.327 Y247.332 Z22 E15485.19069 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X245.98 Y247.421 Z22 E15487.930648 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X247.192 Y247.399 Z22 E15492.970389 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X247.755 Y247.296 Z22 E15495.34992 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X248.799 Y246.923 Z22 E15499.959076 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X249.741 Y246.354 Z22 E15504.534471 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X250.592 Y245.618 Z22 E15509.21218 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X251.328 Y244.767 Z22 E15513.889889 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X251.897 Y243.825 Z22 E15518.465283 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X252.27 Y242.781 Z22 E15523.074439 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X252.373 Y242.218 Z22 E15525.45397 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X252.395 Y241.006 Z22 E15530.493711 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X252.306 Y240.353 Z22 E15533.233669 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X251.909 Y238.95 Z22 E15539.295691 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X251.593 Y238.197 Z22 E15542.690794 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X250.709 Y236.583 Z22 E15550.341588 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X250.132 Y235.719 Z22 E15554.661055 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X248.692 Y233.872 Z22 E15564.398 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X246.844 Y231.859 Z22 E15575.75896 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X244.557 Y229.669 Z22 E15588.923571 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X243.032 Y227.864 Z22 E15598.747679 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X241.477 Y226.251 Z22 E15608.062552 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X238.391 Y223.381 Z22 E15625.583562 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X235.86 Y221.261 Z22 E15639.309893 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X231.405 Y217.938 Z22 E15662.41662 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X228.027 Y215.72 Z22 E15679.217519 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X224.346 Y213.578 Z22 E15696.923819 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X220.382 Y211.576 Z22 E15715.386799 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X218.884119 Y210.939268 Z22 E15722.153565 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010
G1 X216.157 Y209.78 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=end-early tail
G1 X214.242786 Y209.084317 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0010 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0010
G0 X214.242786 Y209.084317 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0011 note=intra-page lift
G0 X207.54993 Y211.811442 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0011 note=intra-page XY
G0 X207.54993 Y211.811442 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0011 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0011
G1 X207.487 Y211.657 Z22 E15722.157419 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X206.983913 Y212.891667 Z22 E15722.465379 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X206.494 Y214.094 Z22 E15723.238755 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X206.427122 Y214.284275 Z22 E15723.40082 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X205.929725 Y215.699406 Z22 E15724.959889 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X205.432329 Y217.114537 Z22 E15727.142585 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X204.934933 Y218.529669 Z22 E15729.948909 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X204.777 Y218.979 Z22 E15730.970413 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X204.494876 Y219.963079 Z22 E15733.37886 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X204.081495 Y221.404993 Z22 E15737.432439 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X203.668115 Y222.846907 Z22 E15742.109646 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X203.39 Y223.817 Z22 E15745.607302 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X203.27984 Y224.295307 Z22 E15747.41048 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X202.943183 Y225.757039 Z22 E15753.334941 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=prime ramp
G1 X202.302 Y228.541 Z22 E15765.212315 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X201.481 Y233.079 Z22 E15784.385404 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X200.896 Y237.363 Z22 E15802.3615 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X200.39 Y243.159 Z22 E15826.550122 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X200.238 Y247.991 Z22 E15846.649181 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X200.279 Y250.56 Z22 E15857.331202 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X200.477 Y253.262 Z22 E15868.594933 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X200.408 Y256.893 Z22 E15883.693602 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X200.525 Y260.025 Z22 E15896.724028 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X200.813 Y262.691 Z22 E15907.872454 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X201.016 Y263.859 Z22 E15912.80123 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X201.532 Y265.886 Z22 E15921.497286 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X201.841 Y266.753 Z22 E15925.323941 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X202.552 Y268.213 Z22 E15932.075422 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X202.95 Y268.814 Z22 E15935.072311 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X203.823 Y269.78 Z22 E15940.485527 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X204.295 Y270.153 Z22 E15942.986656 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X205.296 Y270.696 Z22 E15947.721208 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X206.365 Y270.999 Z22 E15952.340675 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X207.487 Y271.093 Z22 E15957.021751 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X208.609 Y270.999 Z22 E15961.702827 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X209.678 Y270.696 Z22 E15966.322295 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X210.679 Y270.153 Z22 E15971.056847 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X211.151 Y269.78 Z22 E15973.557976 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X212.024 Y268.814 Z22 E15978.971192 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X212.422 Y268.213 Z22 E15981.968081 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X213.133 Y266.753 Z22 E15988.719562 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X213.442 Y265.886 Z22 E15992.546217 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X213.958 Y263.859 Z22 E16001.242273 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X214.161 Y262.691 Z22 E16006.171049 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X214.449 Y260.025 Z22 E16017.319475 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X214.566 Y256.893 Z22 E16030.3499 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X214.497 Y253.262 Z22 E16045.44857 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X214.695 Y250.56 Z22 E16056.712301 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X214.736 Y247.991 Z22 E16067.394322 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X214.584 Y243.159 Z22 E16087.493381 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X214.078 Y237.363 Z22 E16111.682003 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X213.493 Y233.079 Z22 E16129.658098 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X212.672 Y228.541 Z22 E16148.831187 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X211.584 Y223.817 Z22 E16168.985464 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X210.197 Y218.979 Z22 E16189.909802 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X209.320675 Y216.485788 Z22 E16200.897021 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011
G1 X208.48 Y214.094 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=end-early tail
G1 X207.54993 Y211.811442 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0011 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0011
G0 X207.54993 Y211.811442 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0012 note=intra-page lift
G0 X207.707694 Y260.809309 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0012 note=intra-page XY
G0 X207.707694 Y260.809309 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0012 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0012
G1 X206.207702 Y260.814139 Z22 E16201.208834 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X204.70771 Y260.818968 Z22 E16202.144276 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X203.207718 Y260.823798 Z22 E16203.703345 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X203.145 Y260.824 Z22 E16203.782115 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X202.087 Y261.036 Z22 E16205.308054 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X201.766495 Y261.196063 Z22 E16205.886041 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X201.24 Y261.459 Z22 E16206.912717 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X200.896 Y261.75 Z22 E16207.763654 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X200.628188 Y262.125139 Z22 E16208.692365 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X200.367 Y262.491 Z22 E16209.654825 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X200.049 Y263.443 Z22 E16212.005959 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X200.042421 Y263.489302 Z22 E16212.122316 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X199.97 Y263.999 Z22 E16213.443264 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X199.97 Y264.984183 Z22 E16216.175895 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X199.97 Y266.484183 Z22 E16220.853102 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X199.97 Y267.984183 Z22 E16226.153936 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X199.97 Y269.484183 Z22 E16232.078397 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=prime ramp
G1 X199.97 Y272.683 Z22 E16245.377535 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X200.182 Y273.741 Z22 E16249.863625 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X200.605 Y274.588 Z22 E16253.799759 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X201.24 Y275.223 Z22 E16257.533316 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X201.637 Y275.461 Z22 E16259.457725 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X202.589 Y275.779 Z22 E16263.630655 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X203.145 Y275.858 Z22 E16265.965451 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X211.829 Y275.858 Z22 E16302.069328 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X212.887 Y275.646 Z22 E16306.555417 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X213.734 Y275.223 Z22 E16310.491552 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X214.078 Y274.932 Z22 E16312.364821 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X214.607 Y274.191 Z22 E16316.150039 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X214.925 Y273.239 Z22 E16320.322968 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X215.004 Y272.683 Z22 E16322.657765 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X215.03 Y264.608 Z22 E16356.229888 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X214.925 Y263.443 Z22 E16361.093027 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X214.607 Y262.491 Z22 E16365.265957 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X214.369 Y262.094 Z22 E16367.190366 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X213.734 Y261.459 Z22 E16370.923923 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X213.337 Y261.221 Z22 E16372.848332 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X212.686574 Y261.003736 Z22 E16375.699362 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012
G1 X212.385 Y260.903 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=end-early tail
G1 X211.22 Y260.798 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=end-early tail
G1 X207.707694 Y260.809309 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0012 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0012
G0 X207.707694 Y260.809309 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0013 note=intra-page lift
G0 X266.724 Y209.104 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0013 note=intra-page XY
G0 X266.724 Y209.104 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0013 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0013
G1 X267.465 Y209.633 Z22 E16375.814238 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X268.024177 Y209.819784 Z22 E16376.011176 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X268.417 Y209.951 Z22 E16376.207134 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X268.973 Y210.03 Z22 E16376.548785 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X269.497257 Y210.03 Z22 E16376.946617 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X270.997257 Y210.03 Z22 E16378.505686 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X272.497257 Y210.03 Z22 E16380.688383 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X273.997257 Y210.03 Z22 E16383.494707 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X275.497257 Y210.03 Z22 E16386.924658 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X276.997257 Y210.03 Z22 E16390.978237 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X277.657 Y210.03 Z22 E16392.958582 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X278.48088 Y209.864913 Z22 E16395.655443 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X278.715 Y209.818 Z22 E16396.45751 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X279.562 Y209.395 Z22 E16399.793292 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X279.802092 Y209.191899 Z22 E16400.956277 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X279.906 Y209.104 Z22 E16401.468097 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X280.435 Y208.363 Z22 E16405.024012 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X280.578664 Y207.932911 Z22 E16406.880739 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=prime ramp
G1 X280.753 Y207.411 Z22 E16409.168446 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X280.832 Y206.855 Z22 E16411.503243 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X280.858 Y198.78 Z22 E16445.075366 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X280.753 Y197.615 Z22 E16449.938505 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X280.435 Y196.663 Z22 E16454.111435 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X280.197 Y196.266 Z22 E16456.035844 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X279.562 Y195.631 Z22 E16459.769401 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X279.165 Y195.393 Z22 E16461.69381 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X278.213 Y195.075 Z22 E16465.86674 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X277.048 Y194.97 Z22 E16470.729879 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X268.973 Y194.996 Z22 E16504.302002 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X267.915 Y195.208 Z22 E16508.788092 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X267.068 Y195.631 Z22 E16512.724226 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X266.724 Y195.922 Z22 E16514.597496 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X266.195 Y196.663 Z22 E16518.382713 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X265.877 Y197.615 Z22 E16522.555643 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X265.798 Y198.171 Z22 E16524.890439 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X265.798 Y204.331356 Z22 E16550.502225 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013
G1 X265.798 Y206.855 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=end-early tail
G1 X266.01 Y207.913 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=end-early tail
G1 X266.433 Y208.76 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=end-early tail
G1 X266.724 Y209.104 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0013 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0013
G0 X266.724 Y209.104 Z26 F7200 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0014 note=intra-page lift
G0 X213.734 Y143.567 Z26 F7200 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0014 note=intra-page XY
G0 X213.734 Y143.567 Z22 F7200 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0014 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0014
G1 X214.078 Y143.276 Z22 E16550.53036 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X214.607 Y142.535 Z22 E16550.758936 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X214.651031 Y142.403185 Z22 E16550.814039 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X214.925 Y141.583 Z22 E16551.277181 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X215.004 Y141.027 Z22 E16551.688965 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X215.004237 Y140.953317 Z22 E16551.74948 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X215.009067 Y139.453325 Z22 E16553.308549 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X215.013897 Y137.953333 Z22 E16555.491245 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X215.018726 Y136.453341 Z22 E16558.297569 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X215.023556 Y134.953349 Z22 E16561.727521 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X215.028386 Y133.453356 Z22 E16565.781099 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X215.03 Y132.952 Z22 E16567.27502 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X214.940357 Y131.95739 Z22 E16570.458306 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X214.925 Y131.787 Z22 E16571.03138 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X214.607 Y130.835 Z22 E16574.556931 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X214.439783 Y130.556071 Z22 E16575.75914 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X214.369 Y130.438 Z22 E16576.276869 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X213.734 Y129.803 Z22 E16579.783096 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X213.337 Y129.565 Z22 E16581.677629 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X213.335637 Y129.564545 Z22 E16581.683602 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=prime ramp
G1 X212.385 Y129.247 Z22 E16585.850558 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X211.22 Y129.142 Z22 E16590.713698 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X203.145 Y129.168 Z22 E16624.28582 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X202.087 Y129.38 Z22 E16628.77191 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X201.24 Y129.803 Z22 E16632.708045 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X200.605 Y130.438 Z22 E16636.441601 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X200.367 Y130.835 Z22 E16638.366011 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X200.049 Y131.787 Z22 E16642.53894 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X199.97 Y132.343 Z22 E16644.873737 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X199.97 Y141.027 Z22 E16680.977613 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X200.182 Y142.085 Z22 E16685.463703 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X200.605 Y142.932 Z22 E16689.399837 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X201.24 Y143.567 Z22 E16693.133394 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X201.637 Y143.805 Z22 E16695.057804 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X202.589 Y144.123 Z22 E16699.230733 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X203.145 Y144.202 Z22 E16701.565529 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X208.854782 Y144.202 Z22 E16725.304046 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014
G1 X211.829 Y144.202 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=end-early tail
G1 X212.887 Y143.99 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=end-early tail
G1 X213.734 Y143.567 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0014 note=end-early tail
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0014
; CLAYLINE_BODY_END
; CLAYLINE_PROFILE_END_BEGIN
M83 ;Set to Relative Extrusion Mode
G91 ;Set to Relative Positioning
G1 Z150 E-3000 F40000 ;Move Z Axis up and depressurize Extruder slightly
G90 ;Set to Absolute Positioning
G28 Z ;Home Z
G1 X207.5 Y0 F500 ;Move X and Y slow to home position
M82 ;absolute extrusion mode
; CLAYLINE_PROFILE_END_END
