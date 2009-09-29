
class TagSet(object):
    @staticmethod
    def from_json(data, mint, value_key='value'):
        return TagSet( [Tag.from_json(tag_datum, mint=mint, value_key=value_key) for tag_datum in data], mint=mint )

    def __init__(self, tags, mint=None):
        self.mint = mint

        self.tags = list(tags)
        self.tags_set = set(tags)
        self.tags_value = dict((t.value, t) for t in self.tags)
        self.tags_id = dict((t.id, t) for t in self.tags)
        self.order_tags()

    def add(self, tag):
        self.tags.append(tag)
        self.tags_set.add(tag)
        self.tags_value[tag.value] = tag
        self.tags_id[tag.id] = tag
        self.order_tags()

    def remove(self, key):
        tag = self[key]
        self.tags.remove(tag)
        self.tags_set.remove(tag)
        del self.tags_value[tag.value]
        del self.tags_id[tag.id]

    def order_tags(self):
        self.tags.sort(key=lambda x: -len(x.value))

    def __getitem__(self, key):
        if key in self.tags_value:
            return self.tags_value[key]
        if key in self.tags_id:
            return self.tags_id[key]
        raise KeyError(key)

    def __contains__(self, obj):
        return obj in self.tags_set

    def __len__(self):
        return len(self.tags)

    def __str__(self):
        return str(self.tags)

    def parse(self, label):
        tags = []
        for tag in self.tags:
            if label.find(tag.value) == -1:
                continue
            tags.append(tag)
            label = label.replace(tag.value, '', 1).strip()
        assert len(label) == 0
        return TagSet(tags)

    def __iter__(self):
        for t in self.tags:
            yield t

class Tag(object):
    @staticmethod
    def from_json(data, mint, value_key='value'):
        return Tag(data['id'], data[value_key], mint=mint)
    
    def __repr__(self):
        return '<Tag: %s>' % unicode(self)

    def __unicode__(self):
        return self.value
        
    def __init__(self, id, value, mint):
        self.mint = mint

        self.id = id
        self.value = value

    def delete(self):
        self.mint.delete_tag(tagId=self.id)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.id == other.id

    def __hash__(self):
        return self.id
