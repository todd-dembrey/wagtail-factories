from collections import defaultdict

import factory
from factory.declarations import ParameteredAttribute
from wagtail.wagtailcore import blocks

__all__ = [
    'CharBlockFactory',
    'IntegerBlockFactory',
    'StreamFieldFactory',
    'ListBlockFactory',
    'StructBlockFactory',
]


class StreamFieldFactory(ParameteredAttribute):
    """
        Syntax:
            <streamfield>__<index>__<block_name>__<key>='foo',

    """
    def __init__(self, factories, **kwargs):
        super(StreamFieldFactory, self).__init__(**kwargs)
        self.factories = factories

    def generate(self, sequence, obj, create, params):

        result = defaultdict(lambda: defaultdict(lambda: defaultdict()))

        for key, value in params.items():
            try:
                index, block_name, param = key.split('__', 2)
            except ValueError:
                continue
            if not index.isdigit():
                continue

            index = int(index)
            result[index][block_name][param] = value

        retval = []
        for index, block_items in sorted(result.items()):
            for block_name, block_params in block_items.items():
                try:
                    block_factory = self.factories[block_name]
                except KeyError:
                    raise ValueError(
                        "No factory defined for block `%s`" % block_name)

                if callable(block_factory):
                    value = block_factory(**block_params)
                else:
                    value = block_factory.evaluate(index, obj, create, block_params)
                retval.append((block_name, value))
        return retval


class ListBlockFactory(factory.SubFactory):
    def generate(self, sequence, obj, create, params):
        subfactory = self.get_factory()

        result = defaultdict(dict)
        for key, value in params.items():
            if key.isdigit():
                result[int(key)]['value'] = value
            else:
                prefix, label = key.split('__', 2)
                if prefix and prefix.isdigit():
                    result[int(prefix)][label] = value

        retval = []
        for index, index_params in sorted(result.items()):
            item = subfactory(**index_params)
            retval.append(item)
        return retval


class BlockFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        return model_class().clean(kwargs['value'])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class().clean(kwargs['value'])


class CharBlockFactory(BlockFactory):
    class Meta:
        model = blocks.CharBlock


class IntegerBlockFactory(BlockFactory):
    class Meta:
        model = blocks.IntegerBlock


class StructBlockFactory(factory.Factory):

    class Meta:
        model = blocks.StructBlock

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        return model_class().to_python(kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class().to_python(kwargs)