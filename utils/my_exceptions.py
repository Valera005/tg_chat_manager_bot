




class ProfileNotFound(Exception):
    def __init__(self):
        super().__init__(f"Profile was not found")


class NotEnoughRank(Exception):
    def __init__(self, rank_required, command_id):
        self.rank_required = rank_required
        self.command_id = command_id
        super().__init__(f"Not enough rank")