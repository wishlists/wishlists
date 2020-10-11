"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyInteger
from service.models import Wishlist, Item


class WishlistFactory(factory.Factory):
    """ Creates fake wishlists that you don't have to feed """

    class Meta:
        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    user_id = FuzzyInteger(0, 1000)
    items = [Item(product_name='laptop', product_id=1),Item(product_name='iPhone', product_id=2)]


if __name__ == "__main__":
    for _ in range(10):
        wishlist = WishlistFactory()
        print(wishlist.serialize())
