"""A robot drives towards a wall and stops at a safe distance.

Three "nodes" talk to each other only through topics:

    sensor node  --/scan-->  controller node  --/cmd_vel-->  robot (motor driver)

Extra subscribers ("ros2 topic echo") print the messages into the log window.
Use the checkboxes to subscribe/unsubscribe at runtime and watch what happens.
"""


import tkinter as tk
from topic import Topic

CANVAS_W, CANVAS_H = 640, 160
ROBOT_R = 20
SAFE_DISTANCE = 60
WARNING_DISTANCE = 30
MAX_SPEED = 150
GAIN = 2.0
DT = 0.05

# Topics
scan_topic = Topic("/scan")
cmd_vel_topic = Topic("/cmd_vel")
battery_topic = Topic("/battery")

# Robot state
robot = {
    "x": 60.0,
    "v": 0.0,
    "crashed": False,
    "battery": 100.0,
}


def main():
    root = tk.Tk()
    root.title("Robot Pub/Sub Demo")
    root.resizable(False, False)

    canvas = tk.Canvas(
        root, width=CANVAS_W, height=CANVAS_H, bg="white"
    )
    canvas.pack(padx=10, pady=10)

    wall_x = tk.IntVar(value=500)

    tk.Scale(
        root,
        from_=150,
        to=CANVAS_W - 20,
        orient="horizontal",
        length=CANVAS_W,
        label="Wall position (drag me)",
        variable=wall_x,
    ).pack(padx=10)

    panel = tk.Frame(root)
    panel.pack(fill="x", padx=10, pady=5)

    info = tk.Label(root, font=("Consolas", 10))
    info.pack(anchor="w", padx=10)

    warning_label = tk.Label(
        root, text="Waiting for scan...",
        font=("Arial", 12, "bold"), fg="green"
    )
    warning_label.pack(anchor="w", padx=10, pady=3)

    battery_label = tk.Label(
        root, text="Battery: 100.0%",
        font=("Arial", 12, "bold"), fg="darkgreen"
    )
    battery_label.pack(anchor="w", padx=10, pady=3)

    log = tk.Text(root, height=10, width=80, font=("Consolas", 9))
    log.pack(padx=10, pady=10)

    # Robot motor subscriber: receives /cmd_vel
    def motor_callback(velocity):
        robot["v"] = velocity

    # Controller subscriber: receives /scan and publishes /cmd_vel
    def controller_callback(distance):
        velocity = GAIN * (distance - SAFE_DISTANCE)
        velocity = max(-MAX_SPEED, min(MAX_SPEED, velocity))

        if distance <= SAFE_DISTANCE:
            velocity = 0.0

        cmd_vel_topic.publish(velocity)

    # Exercise 1: warning subscriber on /scan
    def warning_callback(distance):
        if distance < WARNING_DISTANCE:
            warning_label.config(
                text=f"WARNING! Distance: {distance:.1f} px",
                fg="red",
            )
        else:
            warning_label.config(
                text=f"Distance safe: {distance:.1f} px",
                fg="green",
            )

    # Exercise 2: subscriber displaying /battery
    def battery_callback(level):
        battery_label.config(text=f"Battery: {level:.1f}%")
        battery_label.config(
            fg="red" if level <= 20 else "darkgreen"
        )

    # Optional topic echo subscribers
    def echo(topic):
        def callback(message):
            log.insert(
                "end", f"[{topic.name}] {message:7.1f}\n"
            )

            if int(log.index("end-1c").split(".")[0]) > 200:
                log.delete("1.0", "2.0")

            log.see("end")

        return callback

    def update_info():
        info.config(
            text=(
                f"/scan: {scan_topic.subscriber_count()} subscribers   "
                f"/cmd_vel: {cmd_vel_topic.subscriber_count()} subscribers   "
                f"/battery: {battery_topic.subscriber_count()} subscribers"
            )
        )

    # Checkboxes allow subscribers to be enabled/disabled at runtime.
    def add_subscription_checkbox(
        text, topic, callback, enabled=True
    ):
        var = tk.BooleanVar(value=enabled)

        def toggle():
            if var.get():
                topic.subscribe(callback)
            else:
                topic.unsubscribe(callback)
            update_info()

        tk.Checkbutton(
            panel, text=text, variable=var, command=toggle
        ).pack(side="left")

        toggle()

    add_subscription_checkbox(
        "controller <- /scan", scan_topic, controller_callback
    )
    add_subscription_checkbox(
        "motor <- /cmd_vel", cmd_vel_topic, motor_callback
    )
    add_subscription_checkbox(
        "warning <- /scan", scan_topic, warning_callback
    )
    add_subscription_checkbox(
        "battery display", battery_topic, battery_callback
    )
    add_subscription_checkbox(
        "echo /scan", scan_topic, echo(scan_topic), enabled=False
    )
    add_subscription_checkbox(
        "echo /cmd_vel", cmd_vel_topic, echo(cmd_vel_topic),
        enabled=False
    )
    add_subscription_checkbox(
        "echo /battery", battery_topic, echo(battery_topic),
        enabled=False
    )

    state = {"battery_elapsed": 0.0}

    def reset():
        robot.update(x=60.0, v=0.0, crashed=False, battery=100.0)
        state["battery_elapsed"] = 0.0
        log.delete("1.0", "end")
        warning_label.config(text="Waiting for scan...", fg="green")
        battery_label.config(text="Battery: 100.0%", fg="darkgreen")

    tk.Button(panel, text="Reset robot", command=reset).pack(side="right")

    def draw():
        canvas.delete("all")
        y = CANVAS_H / 2
        x = robot["x"]
        w = wall_x.get()

        canvas.create_rectangle(
            w, 10, w + 15, CANVAS_H - 10, fill="gray30"
        )
        canvas.create_line(
            w - SAFE_DISTANCE, 10,
            w - SAFE_DISTANCE, CANVAS_H - 10,
            dash=(4, 4), fill="green"
        )
        canvas.create_line(
            x + ROBOT_R, y, w, y,
            fill="red", dash=(2, 2)
        )
        color = "red" if robot["crashed"] else "steelblue"
        canvas.create_oval(
            x - ROBOT_R, y - ROBOT_R,
            x + ROBOT_R, y + ROBOT_R,
            fill=color
        )
        canvas.create_text(
            x, y - ROBOT_R - 12,
            text=f"v = {robot['v']:.0f} px/s"
        )

        if robot["crashed"]:
            canvas.create_text(
                CANVAS_W / 2, 20,
                text="CRASH !!!", fill="red",
                font=("Arial", 16, "bold")
            )

    def tick():
        # Sensor publishes distance to wall.
        w = wall_x.get()
        distance = w - robot["x"] - ROBOT_R
        scan_topic.publish(distance)

        # Apply motor velocity.
        robot["x"] += robot["v"] * DT
        robot["x"] = max(ROBOT_R, robot["x"])

        # Collision protection.
        robot["crashed"] = robot["x"] + ROBOT_R >= w
        if robot["crashed"]:
            robot["x"] = w - ROBOT_R
            robot["v"] = 0.0

        # Publish battery once per second.
        state["battery_elapsed"] += DT
        if state["battery_elapsed"] >= 1.0:
            state["battery_elapsed"] -= 1.0
            robot["battery"] = max(0.0, robot["battery"] - 1.0)
            battery_topic.publish(robot["battery"])

        draw()
        root.after(int(DT * 1000), tick)

    tick()
    root.mainloop()


if __name__ == "__main__":
    main()
