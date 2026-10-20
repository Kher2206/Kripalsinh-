# Observer pattern – a tiny ROS2-style pub/sub demo

Run: `python main.py` (only needs the standard library / tkinter).

A robot drives towards a wall and stops at a safe distance. The parts never call
each other directly; they only publish to and subscribe to topics:

```
sensor (timer) --/scan--> controller --/cmd_vel--> motor
                   \                       \
                    echo /scan              echo /cmd_vel
```

| Observer pattern      | ROS2                           | This code                   |
|-----------------------|--------------------------------|-----------------------------|
| Subject               | Topic                          | `Topic`                     |
| attach / detach       | create/destroy subscription    | `subscribe` / `unsubscribe` |
| notify                | `publisher.publish(msg)`       | `Topic.publish(msg)`        |
| Observer.update       | subscription callback          | any function `f(msg)`       |

## Things to try
1. Drag the wall: the robot follows and keeps the distance.
2. Untick **controller ← /scan**: the motor keeps its last command and the robot crashes.
   Tick it again: it recovers. The sensor doesn't know or care who is listening.
3. Turn on **echo /scan** and **echo /cmd_vel** to watch the messages (like `ros2 topic echo`).

## Exercises
- Add a subscriber to `/scan` that shows a warning label when the distance is < 30 px.
- Add a new topic `/battery` that the robot publishes, and a subscriber that displays it.
- Why does `publish` iterate over `list(self._callbacks)` instead of `self._callbacks`?
