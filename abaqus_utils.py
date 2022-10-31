def derived_values(r_in, r_out, width, num_spokes, spoke_width):
    s_pt_whole = (0.0, r_out, width / 2)
    s_pt_lateral = (0.0, r_out, width / 2)
    s_pt_extr = (0.0, (r_in + r_out) / 2, width)
    s_pt_out_edge = (0.0, r_out, width)

    spoke_start = (r_out + r_in) / 2
    s_pts_spoke = [(-spoke_start + 0.01, spoke_width / 2),
                           (-spoke_start + 0.01, -spoke_width / 2),
                           (-spoke_start, 0),
                           (spoke_start, 0)]

    rot_angle = 180 / num_spokes

    return s_pt_whole, s_pt_lateral, s_pt_extr, s_pt_out_edge, spoke_start, s_pts_spoke, rot_angle