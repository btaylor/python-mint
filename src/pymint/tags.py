from pymint.utils import *

class TagSet(object):
    @staticmethod
    def from_json(data, mint, name_key='value'):
        return TagSet( [Tag.from_json(tag_datum, mint=mint, name_key=name_key) for tag_datum in data], mint=mint )

    def __copy__(self):
        return TagSet(self.tags, self.mint)

    def __init__(self, tags, mint=None):
        self.mint = mint

        self.tags = list(tags)
        self.tags_set = set(tags)
        self.tags_name = dict((t.name, t) for t in self.tags)
        self.tags_id = dict((t.id, t) for t in self.tags)
        self.order_tags()

    def __eq__(self, other):
        if not isinstance(other, TagSet):
            return False
        return self.tags_set == other.tags_set

    def diff(self, new):
        added, removed = TagSet([], self.mint), TagSet([], self.mint)
        for tag in self:
            if tag not in new:
                removed.add(tag)
        for tag in new:
            if tag not in self:
                added.add(tag)
        return added, removed

    def add(self, tag):
        assert tag.id
        if tag not in self.tags_set:
            self.tags.append(tag)
            self.tags_set.add(tag)
            self.tags_name[tag.name] = tag
            self.tags_id[tag.id] = tag
            self.order_tags()

    def remove(self, key):
        tag = self[key]
        self.tags.remove(tag)
        self.tags_set.remove(tag)
        del self.tags_name[tag.name]
        del self.tags_id[tag.id]

    def order_tags(self):
        self.tags.sort(key=lambda x: -len(x.name))

    def __getitem__(self, key):
        if key in self.tags_name:
            return self.tags_name[key]
        if key in self.tags_id:
            return self.tags_id[key]
        raise KeyError(key)

    def __contains__(self, obj):
        if isiterable(obj):
            return all(o in self.tags_set for o in obj)
        return obj in self.tags_set

    def __len__(self):
        return len(self.tags)

    def __repr__(self):
        return '<TagSet: %s>' % str(self)

    def __str__(self):
        return str(self.tags)

    def parse(self, label):
        tags = []
        for tag in self.tags:
            if label.find(tag.name) == -1:
                continue
            tags.append(tag)
            label = label.replace(tag.name, '', 1).strip()
        assert len(label) == 0
        return TagSet(tags)

    def __iter__(self):
        for t in self.tags:
            yield t


class Tag(Flyweight):
    @staticmethod
    def from_json(data, mint, name_key='name'):
        return Tag(data['id'], data[name_key], mint=mint) 

    def __repr__(self):
        return '<Tag: %s>' % unicode(self)

    def __unicode__(self):
        return self.name
   
    def __init__(self, id, name, mint):
        self.id = id
        self.name = name
        self.mint = mint

    def delete(self):
        self.mint.delete_tag(tagId=self.id)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.id == other.id

    def __hash__(self):
        return self.id
