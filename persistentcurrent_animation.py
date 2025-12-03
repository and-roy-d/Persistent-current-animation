from manim import *
import numpy as np


class SuperconductingLoops(Scene):
    def construct(self):
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
        COLOR_DIAL_FILL = GRAY_A  # Light gray for dial background

        # Fonts
        FONT_NAME = "Arial"
        FONT_SIZE = 16

        # Dimensions
        LOOP_W = 3.0
        LOOP_H = 2.0
        WIRE_THICKNESS = 8
        DIAL_RADIUS = 0.8  # Increased radius for better visibility

        # Arrow Styling
        ARROW_STROKE = 10  # Thicker stroke for more visible tails
        ARROW_SCALE = 0.25  # Slightly larger overall
        ARROW_TIP_RATIO = 0.2  # Smaller tip relative to tail length

        # Physics / Animation Constants
        LASER_RADIUS = 0.25
        TIME_SCALE = 1.2
        LINEAR_SPEED = 2.0

        centers = [LEFT * 4, ORIGIN, RIGHT * 4]

        # Dial Logic: 0 is UP (PI/2).
        init_values = [1.0, 1.5, 0.7]
        final_values = [-1.0, -1.5, -0.7]

        def val_to_angle(v):
            # Map values to angles between 0 and PI (for half circle)
            # PI/2 is center (up). Range is roughly PI/6 to 5*PI/6
            return PI / 2 - (v * PI / 6)

        start_angles = [val_to_angle(v) for v in init_values]
        zero_angle = PI / 2
        target_angles = [val_to_angle(v) for v in final_values]

        # -----------------------
        # 2. Geometry Setup
        # -----------------------
        loops_grp = VGroup()
        connections_grp = VGroup()
        dials_grp = VGroup()
        text_labels = VGroup()

        # Geometric segments storage
        top_wires = []
        bottom_wires = []
        left_upper_wires = []
        left_lower_wires = []
        right_upper_wires = []
        right_lower_wires = []

        dial_needles = []
        status_texts = []

        for i, c in enumerate(centers):
            # Coordinates
            tl = c + UP * LOOP_H / 2 + LEFT * LOOP_W / 2
            tr = c + UP * LOOP_H / 2 + RIGHT * LOOP_W / 2
            bl = c + DOWN * LOOP_H / 2 + LEFT * LOOP_W / 2
            br = c + DOWN * LOOP_H / 2 + RIGHT * LOOP_W / 2
            lm = c + LEFT * LOOP_W / 2
            rm = c + RIGHT * LOOP_W / 2

            # --- The Loop Segments ---
            top_line = Line(tl, tr, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
            bottom_line = Line(bl, br, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)

            l_up = Line(lm, tl, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
            l_down = Line(lm, bl, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
            r_up = Line(tr, rm, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
            r_down = Line(br, rm, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)

            joints = VGroup(
                Dot(tl, color=COLOR_WIRE, radius=WIRE_THICKNESS / 200),
                Dot(tr, color=COLOR_WIRE, radius=WIRE_THICKNESS / 200),
                Dot(bl, color=COLOR_WIRE, radius=WIRE_THICKNESS / 200),
                Dot(br, color=COLOR_WIRE, radius=WIRE_THICKNESS / 200),
                Dot(lm, color=COLOR_WIRE, radius=WIRE_THICKNESS / 200),
                Dot(rm, color=COLOR_WIRE, radius=WIRE_THICKNESS / 200)
            )

            loops_grp.add(top_line, bottom_line, l_up, l_down, r_up, r_down, joints)

            top_wires.append(top_line)
            bottom_wires.append(bottom_line)
            left_upper_wires.append(l_up)
            left_lower_wires.append(l_down)
            right_upper_wires.append(r_up)
            right_lower_wires.append(r_down)

            # --- The Dial (Half-Circle Odometer Style) ---
            # Moved up significantly for spacing
            dial_pos = c + UP * (LOOP_H / 2 + 1)

            # 1. Dial Background (Light Gray Half-Circle)
            dial_bg = Sector(
                outer_radius=DIAL_RADIUS,
                angle=PI, start_angle=0,
                color=COLOR_DIAL_FILL, fill_opacity=1.0,
                arc_center=dial_pos
            )

            # 2. Green Sector (Wedge from center)
            t_angle = target_angles[i]
            wedge_width = 0.4
            green_wedge = Sector(
                outer_radius=DIAL_RADIUS * 0.95,  # Slightly smaller than background
                start_angle=t_angle - wedge_width / 2,
                angle=wedge_width,
                color=GREEN, fill_opacity=1.0,
                arc_center=dial_pos
            )

            # 3. Ticks and Arc Outline
            ticks = VGroup()
            min_a = PI / 6
            max_a = 5 * PI / 6
            for angle in np.linspace(min_a, max_a, 9):
                vec = np.array([np.cos(angle), np.sin(angle), 0])
                start = dial_pos + vec * (DIAL_RADIUS * 0.8)
                end = dial_pos + vec * (DIAL_RADIUS * 1.0)
                ticks.add(Line(start, end, color=BLACK, stroke_width=1.5))

            dial_arc = Arc(radius=DIAL_RADIUS, angle=PI, start_angle=0, arc_center=dial_pos, color=COLOR_TEXT,
                           stroke_width=2)
            dial_base = Line(dial_pos + LEFT * DIAL_RADIUS, dial_pos + RIGHT * DIAL_RADIUS, color=COLOR_TEXT,
                             stroke_width=2)

            # 4. Needle
            s_angle = start_angles[i]
            start_vec = np.array([np.cos(s_angle), np.sin(s_angle), 0])
            needle = Line(dial_pos, dial_pos + start_vec * (DIAL_RADIUS * 0.9), color=COLOR_NEEDLE, stroke_width=3)
            pivot = Dot(dial_pos, color=COLOR_TEXT, radius=0.05)

            # 5. Labels (Spaced out vertically)
            dev_label = Text(f"QUANTUM DEVICE {i + 1}", font=FONT_NAME, font_size=FONT_SIZE, weight=BOLD, color=BLACK)
            dev_label.next_to(dial_arc, UP, buff=0.2)

            stat_label = Text("IDLE", font=FONT_NAME, font_size=FONT_SIZE, color=COLOR_IDLE)
            # Placed between dial and loop, with more space
            stat_label.move_to(c + UP * (LOOP_H / 2 + 0.6))

            dials_grp.add(VGroup(dial_bg, green_wedge, ticks, dial_arc, dial_base, needle, pivot))
            text_labels.add(dev_label, stat_label)

            dial_needles.append(needle)
            status_texts.append(stat_label)

            # --- Connections ---
            if i < len(centers) - 1:
                start_pt = rm
                end_pt = centers[i + 1] + LEFT * LOOP_W / 2
                conn = Line(start_pt, end_pt, color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
                connections_grp.add(conn)

        # Input/Output Wires
        input_wire = Line(centers[0] + LEFT * LOOP_W / 2 + LEFT * 2, centers[0] + LEFT * LOOP_W / 2,
                          color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
        output_wire = Line(centers[-1] + RIGHT * LOOP_W / 2, centers[-1] + RIGHT * LOOP_W / 2 + RIGHT * 2,
                           color=COLOR_WIRE, stroke_width=WIRE_THICKNESS)
        connections_grp.add(input_wire, output_wire)

        # --- BIAS LABEL ---
        bias_text = Text("BIAS ON", font=FONT_NAME, font_size=FONT_SIZE, weight=BOLD, color=COLOR_BIAS_ON)
        bias_text.next_to(input_wire, UP, buff=0.15)

        self.add(loops_grp, connections_grp, dials_grp, text_labels, bias_text)

        # -----------------------
        # 3. Arrow Factory
        # -----------------------
        def make_arrow_stream(line_geom, direction_vector=RIGHT, density_factor=1.0):
            grp = VGroup()
            length = line_geom.get_length()
            count = max(1, int(length * 1.0 * density_factor))

            for i in range(count):
                a = Arrow(ORIGIN, direction_vector,
                          color=COLOR_ARROW,
                          stroke_width=ARROW_STROKE,  # Thicker stroke for visible tails
                          max_tip_length_to_length_ratio=ARROW_TIP_RATIO,
                          buff=0).scale(ARROW_SCALE)

                def update_flow(mob, dt, ln=line_geom, offset=i / count):
                    if not hasattr(mob, 'phase'): mob.phase = offset
                    mob.phase = (mob.phase + dt * LINEAR_SPEED / ln.get_length()) % 1
                    start = ln.get_start()
                    end = ln.get_end()
                    mob.move_to(start + (end - start) * mob.phase)

                a.add_updater(update_flow)
                grp.add(a)
            return grp

        # -----------------------
        # 4. Phase 1: Bias ON
        # -----------------------
        top_branch_arrows = []
        bottom_branch_arrows = []
        conn_arrows = VGroup()

        for line in connections_grp:
            conn_arrows.add(make_arrow_stream(line))

        for i in range(3):
            # Top Branch
            t_grp = VGroup()
            t_grp.add(make_arrow_stream(left_upper_wires[i], UP, density_factor=2.0))
            t_grp.add(make_arrow_stream(top_wires[i], RIGHT))
            t_grp.add(make_arrow_stream(right_upper_wires[i], DOWN, density_factor=2.0))
            top_branch_arrows.append(t_grp)

            # Bottom Branch
            b_grp = VGroup()
            b_grp.add(make_arrow_stream(left_lower_wires[i], DOWN, density_factor=2.0))
            b_grp.add(make_arrow_stream(bottom_wires[i], RIGHT))
            b_grp.add(make_arrow_stream(right_lower_wires[i], UP, density_factor=2.0))
            bottom_branch_arrows.append(b_grp)

            self.add(t_grp, b_grp)

        self.add(conn_arrows)
        self.play(FadeIn(conn_arrows), *[FadeIn(g) for g in top_branch_arrows + bottom_branch_arrows],
                  run_time=1.0 * TIME_SCALE)

        # -----------------------
        # 5. Phase 2: Laser Sweep
        # -----------------------

        laser_spot = Dot(radius=LASER_RADIUS, color=COLOR_LASER).set_opacity(1.0)
        start_x = centers[0][0] - 3.5
        y_pos = top_wires[0].get_center()[1]
        laser_spot.move_to([start_x, y_pos, 0])

        self.play(FadeIn(laser_spot), run_time=0.4 * TIME_SCALE)

        for i in range(3):
            target_wire = top_wires[i]
            target_arrows = top_branch_arrows[i]
            target_pos = target_wire.get_center()
            needle = dial_needles[i]
            pivot = dials_grp[i][6].get_center()  # Index 6 is the pivot dot

            # Sweep
            dist = np.linalg.norm(target_pos - laser_spot.get_center())
            self.play(
                laser_spot.animate.move_to(target_pos),
                run_time=(dist / 4.0) * TIME_SCALE,
                rate_func=linear
            )

            # Heat Event: Drop Needle to Zero
            curr_angle = start_angles[i]
            angle_diff = zero_angle - curr_angle

            self.play(
                target_wire.animate.set_color(COLOR_HOT),
                FadeOut(target_arrows),
                Rotate(needle, angle=angle_diff, about_point=pivot),
                run_time=0.4 * TIME_SCALE
            )

            self.wait(0.2 * TIME_SCALE)

            # Cool wire
            self.play(
                target_wire.animate.set_color(COLOR_WIRE),
                run_time=0.2 * TIME_SCALE
            )

        # Exit
        final_x = centers[-1][0] + 3.5
        dist = final_x - laser_spot.get_center()[0]
        self.play(
            laser_spot.animate.move_to([final_x, y_pos, 0]),
            run_time=(dist / 4.0) * TIME_SCALE,
            rate_func=linear
        )
        self.play(FadeOut(laser_spot), run_time=0.2 * TIME_SCALE)

        # -----------------------
        # 6. Phase 3: Bias OFF -> Persistent Loop
        # -----------------------

        reverse_top_arrows = VGroup()
        needle_anims = []
        text_anims = []

        for i in range(3):
            # Top Branch REVERSE flow
            rev_r_up = Line(right_upper_wires[i].get_end(), right_upper_wires[i].get_start())
            p_rup = make_arrow_stream(rev_r_up, UP, density_factor=2.0)

            rev_top = Line(top_wires[i].get_end(), top_wires[i].get_start())
            p_top = make_arrow_stream(rev_top, LEFT)

            rev_l_up = Line(left_upper_wires[i].get_end(), left_upper_wires[i].get_start())
            p_lup = make_arrow_stream(rev_l_up, DOWN, density_factor=2.0)

            reverse_top_arrows.add(p_rup, p_top, p_lup)

            # Needle moves Zero -> Negative
            needle = dial_needles[i]
            pivot = dials_grp[i][6].get_center()
            angle_diff = target_angles[i] - zero_angle
            needle_anims.append(Rotate(needle, angle=angle_diff, about_point=pivot))

            # Status Text Fade Transition
            new_stat = Text("TUNED", font=FONT_NAME, font_size=FONT_SIZE, color=COLOR_TUNED)
            new_stat.move_to(status_texts[i].get_center())

            text_anims.append(FadeOut(status_texts[i]))
            text_anims.append(FadeIn(new_stat))

        # Bias Text Fade Transition
        new_bias_text = Text("BIAS OFF", font=FONT_NAME, font_size=FONT_SIZE, weight=BOLD, color=COLOR_BIAS_OFF)
        new_bias_text.move_to(bias_text.get_center())

        self.play(
            FadeOut(conn_arrows),
            FadeIn(reverse_top_arrows),
            FadeOut(bias_text),
            FadeIn(new_bias_text),
            *needle_anims,
            *text_anims,
            run_time=1.5 * TIME_SCALE
        )

        self.wait(3 * TIME_SCALE)