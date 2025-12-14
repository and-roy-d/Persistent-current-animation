from manim import *
import numpy as np


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


class Microcal(Scene):
    def construct(self):
        # Set the default font for all Text objects in this scene
        Text.set_default(font="Inter")
        # --- 1. PHYSICS CONSTANTS ---

        decay_tau = 0.25
        rise_tau = 0.02
        base_time = 0.25

        # Impact times
        t1 = base_time
        t2 = t1 + (2.0 * decay_tau)
        t3 = t2 + (5.0 * decay_tau)

        impact_times = [t1, t2, t3]
        amplitudes = [5.0, 1.0, 3.0]
        photon_colors = [RED, BLUE, YELLOW]

        scroll_window = 2
        # Simulation duration
        sim_end_time = t3 + scroll_window + 0.75

        # Animation speed adjustment (1.25x duration = 80% speed)
        animation_duration = sim_end_time * 1.25

        # --- 2. PRE-CALCULATE DATA (High Res & Double Exp) ---
        # Resolution must be very high to prevent peak jitter
        dt = 0.0005

        # Start time array at negative window so the graph starts "full"
        time_array = np.arange(-scroll_window, sim_end_time, dt)
        temp_array = np.zeros_like(time_array) + 0.5  # Baseline

        # Pre-calculate Normalization Factor for the pulse shape
        # We want the max height to equal exactly 'amplitude'
        # Theoretical peak time for double exp:
        ln_tau = np.log(decay_tau / rise_tau)
        inv_tau = (1 / rise_tau) - (1 / decay_tau)
        t_peak = ln_tau / inv_tau
        peak_val = np.exp(-t_peak / decay_tau) - np.exp(-t_peak / rise_tau)
        norm_factor = 1.0 / peak_val

        for i, t_impact in enumerate(impact_times):
            amp = amplitudes[i]

            # Identify valid times (t > t_impact)
            mask = time_array > t_impact
            dt_rel = time_array[mask] - t_impact

            # Double Exponential Formula: A * (exp(-t/fall) - exp(-t/rise))
            pulse = amp * norm_factor * (np.exp(-dt_rel / decay_tau) - np.exp(-dt_rel / rise_tau))

            temp_array[mask] += pulse

        # --- 3. LAYOUT ---
        bath_line = Line(LEFT * 6 + DOWN * 2, LEFT * 2 + DOWN * 2)
        bath_lbl = Text("Bath", font_size=24).next_to(bath_line, DOWN)

        link_points = [
            bath_line.get_center(), bath_line.get_center() + UP * 0.5,
                                    bath_line.get_center() + UP * 0.7 + LEFT * 0.2,
                                    bath_line.get_center() + UP * 0.9 + RIGHT * 0.2,
                                    bath_line.get_center() + UP * 1.1 + LEFT * 0.2,
                                    bath_line.get_center() + UP * 1.3 + RIGHT * 0.2,
                                    bath_line.get_center() + UP * 1.5, bath_line.get_center() + UP * 2.0
        ]
        link = VMobject().set_points_as_corners(link_points)
        link_lbl = Text("G", font_size=24).next_to(link, RIGHT)

        tes = Square(side_length=1.5).move_to(link_points[-1] + UP * 0.75)
        tes.set_fill(BLUE, opacity=1).set_stroke(WHITE)
        tes_lbl = Text("Detector", font_size=24).move_to(tes)

        # -- Scope Box --
        axes = Axes(
            x_range=[0, scroll_window],
            y_range=[0, 8],
            x_length=6, y_length=4,
            axis_config={"include_tip": False, "include_numbers": False, "stroke_width": 0}
        ).to_edge(RIGHT).shift(LEFT * 0.5)

        box = Rectangle(
            width=axes.x_length,
            height=axes.y_length,
            color=WHITE,
            stroke_width=2
        ).move_to(axes.get_center())

        y_lbl = Text("Temperature", font_size=24).rotate(90 * DEGREES).next_to(box, LEFT, buff=0.3)
        x_lbl = Text("Time", font_size=24).next_to(box, DOWN)

        self.add(bath_line, bath_lbl, link, link_lbl, tes, tes_lbl)
        self.add(axes, box, y_lbl, x_lbl)

        # --- 4. ANIMATION LOGIC ---
        time_tracker = ValueTracker(0)

        # A) TES Color Updater
        tes.add_updater(lambda m: m.set_fill(
            color=interpolate_color(BLUE, RED,
                                    (np.interp(time_tracker.get_value(), time_array, temp_array) - 0.5) / 6.0)
        ))

        # B) Graph Updater
        graph_line = VMobject(color=RED, stroke_width=3)
        self.add(graph_line)
        graph_line.set_z_index(1)

        def update_graph(mob):
            t_now = time_tracker.get_value()
            t_start = t_now - scroll_window

            # Efficient search since time_array is sorted
            idx_start = np.searchsorted(time_array, t_start)
            idx_end = np.searchsorted(time_array, t_now)

            # Slice
            current_times = time_array[idx_start:idx_end]
            current_temps = temp_array[idx_start:idx_end]

            if len(current_times) > 1:
                rel_times = current_times - t_start
                # Vectorized coordinate mapping is not easy in Manim, sticking to list comp
                # But 'current_times' is high res (thousands of points).
                # Optimization: Downsample ONLY for drawing, but keep enough for smoothness
                # We skip every 2nd point to save rendering time while keeping shape
                step = 2
                points = [
                    axes.coords_to_point(t, T)
                    for t, T in zip(rel_times[::step], current_temps[::step])
                ]
                mob.set_points_as_corners(points)

        graph_line.add_updater(update_graph)

        # C) Photons
        photons = VGroup()

        # Directions: Top-Left, Top-Right, Top
        directions = [normalize(UP + LEFT), normalize(UP + RIGHT), UP]
        rotations = [-45 * DEGREES, 45 * DEGREES, 90 * DEGREES]

        for i in range(3):
            p = FunctionGraph(
                lambda x: 0.15 * np.sin(30 * x) * np.exp(-x ** 2 * 5),
                x_range=[-1, 1],
                color=photon_colors[i]
            )
            p.rotate(rotations[i])
            p.hit_time = impact_times[i]
            p.direction = directions[i]
            photons.add(p)

        def update_photons(mob):
            t_now = time_tracker.get_value()
            target = tes.get_center()
            speed = 5.0
            for p in mob:
                dt_hit = p.hit_time - t_now
                if dt_hit > 0:
                    p.move_to(target + p.direction * (speed * dt_hit)).set_opacity(1)
                elif dt_hit > -0.1:
                    p.set_opacity(0)
                else:
                    p.set_opacity(0)

        photons.add_updater(update_photons)
        self.add(photons)

        # --- 5. RUN ---
        # Start at 0, end at sim_end_time
        self.play(
            time_tracker.animate.set_value(sim_end_time),
            run_time=animation_duration,
            rate_func=linear
        )