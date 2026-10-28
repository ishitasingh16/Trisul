import math
from typing import Dict, List, Optional


class TrackedWorldObject:

    def __init__(self, obj_id: int, class_name: str, x: float, y: float, z: float, confidence: float, current_time: float):
        self.id = obj_id
        self.class_name = class_name
        self.x = x
        self.y = y
        self.z = z
        self.confidence = confidence
        self.last_seen_time = current_time
        self.first_seen_time = current_time
        self.hits = 1
        self.is_dynamic = False

    def update(self, new_x: float, new_y: float, new_z: float, conf: float, current_time: float, alpha: float = 0.3, velocity_threshold: float = 0.25):
        dt = current_time - self.last_seen_time
        if dt > 0.05:
            dist = math.hypot(new_x - self.x, new_y - self.y)
            speed = dist / dt
            if speed > velocity_threshold:
                self.is_dynamic = True

        self.x = (1.0 - alpha) * self.x + alpha * new_x
        self.y = (1.0 - alpha) * self.y + alpha * new_y
        self.z = (1.0 - alpha) * self.z + alpha * new_z
        self.confidence = (1.0 - alpha) * self.confidence + alpha * conf
        self.last_seen_time = current_time
        self.hits += 1


class ObjectTracker:

    def __init__(self, association_radius: float = 0.5, stale_timeout_sec: float = 30.0):
        self.association_radius = association_radius
        self.stale_timeout_sec = stale_timeout_sec
        self.objects: Dict[int, TrackedWorldObject] = {}
        self.next_id: int = 1

    def update_or_add(self, class_name: str, x: float, y: float, z: float, confidence: float, current_time: float) -> TrackedWorldObject:
        best_id: Optional[int] = None
        best_dist: float = self.association_radius

        for obj_id, obj in self.objects.items():
            if obj.class_name == class_name:
                dist = math.hypot(obj.x - x, obj.y - y)
                if dist < best_dist:
                    best_dist = dist
                    best_id = obj_id

        if best_id is not None:
            self.objects[best_id].update(x, y, z, confidence, current_time)
            return self.objects[best_id]

        new_obj = TrackedWorldObject(self.next_id, class_name, x, y, z, confidence, current_time)
        self.objects[self.next_id] = new_obj
        self.next_id += 1
        return new_obj

    def prune_stale(self, current_time: float) -> int:
        stale_ids = [
            obj_id for obj_id, obj in self.objects.items()
            if (current_time - obj.last_seen_time) > self.stale_timeout_sec
        ]
        for obj_id in stale_ids:
            del self.objects[obj_id]
        return len(stale_ids)

    def get_objects(self) -> List[TrackedWorldObject]:
        return list(self.objects.values())
