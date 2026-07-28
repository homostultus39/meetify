from services.database.default.seed_admin import seed_admin
from services.database.default.seed_room_time_slots import seed_room_time_slots
from services.database.default.seed_rooms import seed_rooms
from services.database.default.seed_time_slots import seed_time_slots

all = [seed_admin, seed_rooms, seed_room_time_slots, seed_time_slots]