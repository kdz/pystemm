def euler(f_dot, f_prev, t_prev, t, dt):
    if t_prev + dt > t:
        return f_prev
    else:
        return euler(f_dot, f_prev + f_dot(t_prev)*dt, t_prev+dt, t, dt)