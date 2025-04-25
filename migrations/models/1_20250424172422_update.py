from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `TXT` RENAME COLUMN `book_name` TO `name`;
        ALTER TABLE `TXT` RENAME COLUMN `book_title` TO `title`;
        ALTER TABLE `TXT` RENAME COLUMN `book_txt` TO `txt`;
        ALTER TABLE `TXT` RENAME COLUMN `book_nums` TO `nums`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `TXT` RENAME COLUMN `name` TO `book_name`;
        ALTER TABLE `TXT` RENAME COLUMN `txt` TO `book_txt`;
        ALTER TABLE `TXT` RENAME COLUMN `title` TO `book_title`;
        ALTER TABLE `TXT` RENAME COLUMN `nums` TO `book_nums`;"""
