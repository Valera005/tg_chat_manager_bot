class Migration:
    def __init__(self):
        self.migrate_from_chat_id = None
        self.migrate_to_chat_id = None

    def add_migrate_from_chat_id(self, chat_id : int):
        self.migrate_from_chat_id = chat_id

    def add_migrate_to_chat_id(self, chat_id : int):
        self.migrate_to_chat_id = chat_id

    def clear(self):
        self.migrate_from_chat_id = None
        self.migrate_to_chat_id = None

    async def check_migration(self, pool):
        if self.migrate_from_chat_id and self.migrate_to_chat_id:
            migrate_to_chat_id = self.migrate_to_chat_id
            migrate_from_chat_id = self.migrate_from_chat_id
            self.clear()
            async with pool.acquire() as con:
                await con.execute(f'''Update groups set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')
                await con.execute(f'''Update bans set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')
                await con.execute(f'''Update commands set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')
                await con.execute(f'''Update messages set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')
                await con.execute(f'''Update profiles set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')
                await con.execute(f'''Update rewards set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')
                await con.execute(f'''Update users set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')
                await con.execute(f'''Update warns set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')
                await con.execute(f'''Update weddings set chat_id = {migrate_to_chat_id} where chat_id = {migrate_from_chat_id}''')


migration = Migration()


