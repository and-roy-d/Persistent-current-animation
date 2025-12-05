from manim import *
import numpy as np


class SuperconductingLoops(Scene):
    def construct(self):
        # -----------------------
        # 1. Configuration & Style
        # -----------------------
        self.camera.background_color = WHITE

        # Colors
        COLOR_WIRE = BLACK
        COLOR_HOT = RED
        COLOR_LASER = GREEN
        COLOR_ARROW = "#29ABCA"
        COLOR_TEXT = BLACK
        COLOR_NEEDLE = RED
        COLOR_BIAS_ON = ORANGE
        COLOR_BIAS_OFF = GRAY
        COLOR_TUNED = GREEN
        COLOR_IDLE = GRAY
        COLOR_DIAL_FILL = GRAY_A

        # Fonts
        FONT_NAME = "Arial"
        FONT_SIZE = 24

        # --- PHYSICS CONSTANTS ---
        L_RATIO_VAL = 100.0
        L_RATIOS = [L_RATIO_VAL] * 3

        # Sequential Bias Currents
        BIAS_AMPS_RAW = [1.0, 5.0, 9.0]
        MAX_AMP_REF = 10.0
        BIAS_NORMALIZED = [b / MAX_AMP_REF for b in BIAS_AMPS_RAW]

        # --- GEOMETRY VARIABLES ---
        BASE_LOOP_W = 1.6
        WIRE_THICKNESS = 8

        ARC_ANGLE_DEG = 330
        ref_arc_angle_rad = ARC_ANGLE_DEG * DEGREES

        DIAMETER_SPACING = 1.1
        ENABLE_DIAMETER_SCALING = False

        ref_chord_angle = TAU - ref_arc_angle_rad
        base_radius = BASE_LOOP_W / (2 * np.sin(ref_chord_angle / 2))
        DIAL_RADIUS = base_radius * 0.6

        loop_scales = [1.0] * 3
        device_radii = [base_radius * s for s in loop_scales]

        device_angles = []
        for r in device_radii:
            ratio = BASE_LOOP_W / (2 * r)
            ratio = min(1.0, ratio)
            chord_angle = 2 * np.arcsin(ratio)
            device_angles.append(TAU - chord_angle)

        device_widths = [BASE_LOOP_W] * 3

        centers = []
        current_x = 0
        for i, r in enumerate(device_radii):
            if i == 0:
                centers.append(ORIGIN)
            else:
                prev_r = device_radii[i - 1]
                avg_diam = (prev_r + r)
                gap = avg_diam * (DIAMETER_SPACING - 1.0) / 2.0
                dist = prev_r + r + gap
                current_x += dist
                centers.append(RIGHT * current_x)

        total_width_span = centers[-1][0] - centers[0][0]
        centers = [c + LEFT * (total_width_span / 2) for c in centers]

        ARROW_STROKE = 6
        ARROW_TIP_RATIO = 0.25
        ARROW_SCALE_BASE = 0.20

        # Animation & Laser
        LASER_RADIUS = 0.15
        TIME_SCALE = 1.8
        LINEAR_SPEED = 0.7
        LASER_TRAVEL_Y = -2

        # --- CALCULATION HELPER ---
        def get_currents(ratio, i_bias_norm):
            Ls = 1.0
            Ll = ratio
            # Phase 1: Inductive Divider
            I_leak = i_bias_norm * (Ls / (Ll + Ls))
            I_short = i_bias_norm * (Ll / (Ll + Ls))
            # Phase 2: Heat
            I_heat = i_bias_norm
            # Phase 3: Trap
            I_final = i_bias_norm * (Ll / (Ll + Ls))
            return I_leak, I_short, I_heat, I_final

        # --- DIAL LOGIC ---
        def current_to_angle(i_val):
            val = max(0, min(1, i_val))
            return PI - (val * PI)

        wedge_configs = []
        for i in range(3):
            _, _, _, i_final = get_currents(L_RATIOS[i], BIAS_NORMALIZED[i])
            target_angle = current_to_angle(i_final)
            span = 0.2
            w_start = max(0, target_angle - span / 2)
            w_end = min(PI, target_angle + span / 2)
            wedge_configs.append((w_start + (w_end - w_start) / 2, w_end - w_start))

        # -----------------------
        # 2. Geometry Setup
        # -----------------------
        loops_grp = VGroup()
        connections_grp = VGroup()
        dials_grp = VGroup()
        text_labels = VGroup()

        top_wires = []
        bottom_wires = []

        dial_needles = []
        status_texts = []

        for i, c in enumerate(centers):
            w = device_widths[i]
            r = device_radii[i]
            angle_rad = device_angles[i]

            left_pt = c + LEFT * w / 2
            right_pt = c + RIGHT * w / 2

            top_line = Line(left_pt, right_pt, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
            bottom_arc = ArcBetweenPoints(left_pt, right_pt, angle=-angle_rad, color=COLOR_WIRE,
                                          stroke_width=WIRE_THICKNESS)
            joints = VGroup(Dot(left_pt, color=COLOR_WIRE, radius=WIRE_THICKNESS / 200),
                            Dot(right_pt, color=COLOR_WIRE, radius=WIRE_THICKNESS / 200))

            loops_grp.add(top_line, bottom_arc, joints)
            top_wires.append(top_line)
            bottom_wires.append(bottom_arc)

            dial_pos = bottom_arc.get_arc_center()
            dial_bg = Sector(outer_radius=DIAL_RADIUS, angle=PI, start_angle=0, color=COLOR_DIAL_FILL, fill_opacity=1.0,
                             arc_center=dial_pos)
            mid_a, span_a = wedge_configs[i]
            green_wedge = Sector(outer_radius=DIAL_RADIUS * 0.95, start_angle=mid_a - span_a / 2, angle=span_a,
                                 color=GREEN, fill_opacity=1.0, arc_center=dial_pos)

            ticks = VGroup()
            for angle in np.linspace(0, PI, 11):
                vec = np.array([np.cos(angle), np.sin(angle), 0])
                ticks.add(Line(dial_pos + vec * DIAL_RADIUS * 0.8, dial_pos + vec * DIAL_RADIUS, color=BLACK,
                               stroke_width=1.5))

            dial_arc = Arc(radius=DIAL_RADIUS, angle=PI, start_angle=0, arc_center=dial_pos, color=COLOR_TEXT,
                           stroke_width=2)
            dial_base = Line(dial_pos + LEFT * DIAL_RADIUS, dial_pos + RIGHT * DIAL_RADIUS, color=COLOR_TEXT,
                             stroke_width=2)
            needle = Line(dial_pos, dial_pos + LEFT * DIAL_RADIUS * 0.9, color=COLOR_NEEDLE, stroke_width=3)
            pivot = Dot(dial_pos, color=COLOR_TEXT, radius=DIAL_RADIUS * 0.1)

            dev_label = Text(f"DEVICE {i + 1}", font=FONT_NAME, font_size=FONT_SIZE, weight=BOLD, color=BLACK).next_to(
                dial_arc, UP, buff=0.15)
            stat_label = Text("TUNED", font=FONT_NAME, font_size=FONT_SIZE, color=COLOR_TUNED).set_opacity(0).next_to(
                dial_base, DOWN, buff=0.5)

            dials_grp.add(VGroup(dial_bg, green_wedge, ticks, dial_arc, dial_base, needle, pivot))
            text_labels.add(dev_label, stat_label)
            dial_needles.append(needle)
            status_texts.append(stat_label)

            if i < len(centers) - 1:
                next_left_pt = centers[i + 1] + LEFT * device_widths[i + 1] / 2
                conn = Line(right_pt, next_left_pt, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
                connections_grp.add(conn)

        first_pt = top_wires[0].get_start()
        last_pt = top_wires[-1].get_end()
        input_wire = Line(first_pt + LEFT * 2, first_pt, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
        output_wire = Line(last_pt, last_pt + RIGHT * 2, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
        connections_grp.add(input_wire, output_wire)

        bias_text = Text("BIAS OFF", font=FONT_NAME, font_size=FONT_SIZE, weight=BOLD, color=COLOR_BIAS_OFF)
        bias_text.next_to(input_wire, DOWN, buff=2.5)

        all_scene = VGroup(loops_grp, connections_grp, dials_grp, text_labels, bias_text)
        if all_scene.height > config.frame_height * 0.85: all_scene.scale_to_fit_height(config.frame_height * 0.85)
        if all_scene.width > config.frame_width * 0.90: all_scene.scale_to_fit_width(config.frame_width * 0.90)

        all_scene.move_to(ORIGIN).shift(DOWN * 0.5)
        self.add(all_scene)

        # -----------------------
        # 3. Arrow Factory
        # -----------------------
        def make_arrow_stream(line_geom, direction_vector=RIGHT, current_val=1.0):
            grp = VGroup()

            # Robust length calculation
            if isinstance(line_geom, Line):
                length = line_geom.get_length()
            elif isinstance(line_geom, Arc) or isinstance(line_geom, ArcBetweenPoints):
                length = line_geom.get_arc_length()
            else:
                length = 1.0  # Fallback

            if current_val < 0.01: return grp

            # --- DENSITY SCALING ---
            # 8.0 multiplier for robust visual density on all segments
            density = 0.5 + 3 * current_val
            count = int(length * density)

            scale = ARROW_SCALE_BASE

            for i in range(count):
                a = Arrow(ORIGIN, direction_vector, color=COLOR_ARROW, stroke_width=ARROW_STROKE,
                          max_tip_length_to_length_ratio=ARROW_TIP_RATIO, buff=0).scale(scale)

                def update_flow(mob, dt, ln=line_geom, offset=i / count, total_len=length):
                    if not hasattr(mob, 'phase'): mob.phase = offset
                    mob.phase = (mob.phase + dt * LINEAR_SPEED / total_len) % 1

                    try:
                        pos = ln.point_from_proportion(mob.phase)
                        pos_plus = ln.point_from_proportion((mob.phase + 0.01) % 1)
                        angle = angle_of_vector(pos_plus - pos)
                        mob.move_to(pos).rotate(angle - mob.get_angle())
                    except:
                        pass  # Safety for edge cases

                a.add_updater(update_flow)
                grp.add(a)
            return grp

        # -----------------------
        # 4. SEQUENTIAL ANIMATION
        # -----------------------

        tuned_loops_data = []  # Stores {top, bot, val} for tuned loops

        # Laser Setup
        laser_start_x = top_wires[0].get_start()[0] - 2.0
        laser_spot = Dot(radius=LASER_RADIUS, color=COLOR_LASER).set_opacity(0)
        laser_spot.move_to([laser_start_x, LASER_TRAVEL_Y, 0])
        laser_spot.set_z_index(10)
        self.add(laser_spot)

        self.wait(1.0)

        # State tracking references to allow fading out previous arrows
        current_bus_arrows = VGroup()
        current_loop_arrows = [{'top': VGroup(), 'bot': VGroup()} for _ in range(3)]

        for i in range(3):
            # --- PHASE 1: TRANSITION BIAS ---
            target_bias = BIAS_NORMALIZED[i]

            new_bias_text = Text("BIAS ON", font=FONT_NAME, font_size=FONT_SIZE, weight=BOLD, color=COLOR_BIAS_ON)
            new_bias_text.move_to(bias_text.get_center())

            # 1a. New Bus Arrows
            new_bus_arrows = VGroup()
            for line in connections_grp:
                new_bus_arrows.add(make_arrow_stream(line, current_val=target_bias))

            # 1b. Update All Loop Arrows based on new Bias
            new_loop_arrows_anims = []
            new_loop_arrows_refs = []  # To replace current_loop_arrows

            needle_anims = []

            for k in range(3):
                is_tuned = (k < i)

                if is_tuned:
                    stored_val = tuned_loops_data[k]['val']

                    # Top (Short) Current = Bias (Right) - Stored (Left)
                    net_top_val = target_bias - stored_val

                    if net_top_val >= 0:
                        new_top = make_arrow_stream(top_wires[k], RIGHT, current_val=net_top_val)
                    else:
                        rev_geom = Line(top_wires[k].get_end(), top_wires[k].get_start())
                        new_top = make_arrow_stream(rev_geom, LEFT, current_val=abs(net_top_val))

                    # Bot (Loop) Current = Stored (Right) - FIXED
                    new_bot = current_loop_arrows[k]['bot']

                else:
                    # Untuned: Split Bias
                    k_leak, k_short, _, _ = get_currents(L_RATIOS[k], target_bias)
                    new_top = make_arrow_stream(top_wires[k], RIGHT, current_val=k_short)
                    new_bot = make_arrow_stream(bottom_wires[k], RIGHT, current_val=k_leak)

                    # Needle: Moves to Leakage
                    n_pivot = dials_grp[k][6].get_center()
                    n_angle = current_to_angle(k_leak)

                    prev_bias = 0 if i == 0 else BIAS_NORMALIZED[i - 1]
                    if k < i:
                        prev_leak = 0
                    else:
                        prev_leak, _, _, _ = get_currents(L_RATIOS[k], prev_bias)

                    prev_angle = current_to_angle(prev_leak)
                    needle_anims.append(Rotate(dial_needles[k], angle=(n_angle - prev_angle), about_point=n_pivot))

                new_loop_arrows_refs.append({'top': new_top, 'bot': new_bot})

                # Add fade transitions
                if current_loop_arrows[k]['top'] != new_top:
                    new_loop_arrows_anims.append(FadeOut(current_loop_arrows[k]['top']))
                    new_loop_arrows_anims.append(FadeIn(new_top))

                if current_loop_arrows[k]['bot'] != new_bot:
                    new_loop_arrows_anims.append(FadeOut(current_loop_arrows[k]['bot']))
                    new_loop_arrows_anims.append(FadeIn(new_bot))

            self.play(
                Transform(bias_text, new_bias_text),
                FadeOut(current_bus_arrows),
                FadeIn(new_bus_arrows),
                *new_loop_arrows_anims,
                *needle_anims,
                run_time=0.8 * TIME_SCALE
            )

            # Update References
            current_bus_arrows = new_bus_arrows
            current_loop_arrows = new_loop_arrows_refs

            # --- 2. LASER HEAT ---
            target_pos = top_wires[i].get_center()

            self.play(
                laser_spot.animate.set_opacity(1).move_to([target_pos[0], LASER_TRAVEL_Y, 0]),
                run_time=0.5 * TIME_SCALE
            )
            self.play(
                laser_spot.animate.move_to(target_pos),
                run_time=0.3 * TIME_SCALE
            )

            _, _, i_heat, _ = get_currents(L_RATIOS[i], target_bias)

            full_bot_arrow = make_arrow_stream(bottom_wires[i], RIGHT, current_val=i_heat)
            angle_max = current_to_angle(i_heat)

            i_leak_curr, _, _, _ = get_currents(L_RATIOS[i], target_bias)
            angle_leak = current_to_angle(i_leak_curr)

            pivot = dials_grp[i][6].get_center()

            self.play(
                top_wires[i].animate.set_color(COLOR_HOT),
                FadeOut(current_loop_arrows[i]['top']),
                FadeOut(current_loop_arrows[i]['bot']),
                FadeIn(full_bot_arrow),
                Rotate(dial_needles[i], angle=(angle_max - angle_leak), about_point=pivot),
                run_time=0.5 * TIME_SCALE
            )

            current_loop_arrows[i]['bot'] = full_bot_arrow

            self.wait(0.2 * TIME_SCALE)
            self.play(top_wires[i].animate.set_color(COLOR_WIRE), run_time=0.3 * TIME_SCALE)

            self.play(
                laser_spot.animate.move_to([target_pos[0], LASER_TRAVEL_Y, 0]),
                run_time=0.3 * TIME_SCALE
            )

            # --- PHASE 3: MARK AS TUNED ---
            _, _, _, i_final_val = get_currents(L_RATIOS[i], target_bias)

            tuned_loops_data.append({
                'val': i_final_val,
                'max_angle': angle_max
            })

            self.play(status_texts[i].animate.set_opacity(1), run_time=0.5 * TIME_SCALE)

        # --- END OF LOOP: ALL TUNED. TURN OFF BIAS. ---

        off_text = Text("BIAS OFF", font=FONT_NAME, font_size=FONT_SIZE, weight=BOLD, color=COLOR_BIAS_OFF)
        off_text.move_to(bias_text.get_center())

        final_anims = []
        final_anims.append(FadeOut(current_bus_arrows))

        for k in range(3):
            stored_val = tuned_loops_data[k]['val']

            # Bot
            final_bot = make_arrow_stream(bottom_wires[k], RIGHT, current_val=stored_val)
            final_anims.append(FadeOut(current_loop_arrows[k]['bot']))
            final_anims.append(FadeIn(final_bot))

            # Top
            rev_geom = Line(top_wires[k].get_end(), top_wires[k].get_start())
            final_top = make_arrow_stream(rev_geom, LEFT, current_val=stored_val)

            if k < 2:
                final_anims.append(FadeOut(current_loop_arrows[k]['top']))

            final_anims.append(FadeIn(final_top))

            # Needle Drop
            pivot = dials_grp[k][6].get_center()
            curr_a = tuned_loops_data[k]['max_angle']
            target_a = current_to_angle(stored_val)

            final_anims.append(Rotate(dial_needles[k], angle=(target_a - curr_a), about_point=pivot))

        self.play(
            Transform(bias_text, off_text),
            *final_anims,
            run_time=1.5 * TIME_SCALE
        )

        final_exit_x = top_wires[-1].get_end()[0] + 2.0
        self.play(laser_spot.animate.move_to([final_exit_x, LASER_TRAVEL_Y, 0]).set_opacity(0), run_time=1.0)
        self.wait(2.0)