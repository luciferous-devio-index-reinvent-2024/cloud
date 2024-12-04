from .interval_getter import create_interval_getter

client_contentful = create_interval_getter(0.3)
client_notion = create_interval_getter(0.5)

__all__ = ["create_interval_getter", "client_contentful", "client_notion"]
