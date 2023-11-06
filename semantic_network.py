# Guiao de representacao do conhecimento
# -- Redes semanticas
# 
# Inteligencia Artificial & Introducao entity Inteligencia Artificial
# DETI / UA
#
# (c) Luis Seabra Lopes, 2012-2020
# v1.9 - 2019/10/20
#


# Classe Relation, com as seguintes classes derivadas:
#     - Association - uma associacao genérica entre duas entidades
#     - Subtype - uma relacao de subtipo entre dois tipos
#     - Member - uma relacao de pertenca de uma instância entity um tipo
#

class Relation:
    def __init__(self, e1, rel, e2):
        self.entity1 = e1
        #       self.relation = rel  # obsoleto
        self.name = rel
        self.entity2 = e2

    def __str__(self):
        return self.name + "(" + str(self.entity1) + "," + \
            str(self.entity2) + ")"

    def __repr__(self):
        return str(self)


# Subclasse Association
class Association(Relation):
    def __init__(self, e1, assoc, e2):
        Relation.__init__(self, e1, assoc, e2)


#   Exemplo:
#   entity = Association('socrates','professor','filosofia')

# Subclasse Subtype
class Subtype(Relation):
    def __init__(self, sub, super):
        Relation.__init__(self, sub, "subtype", super)


#   Exemplo:
#   s = Subtype('homem','mamifero')

# Subclasse Member
class Member(Relation):
    def __init__(self, obj, type):
        Relation.__init__(self, obj, "member", type)


#   Exemplo:
#   m = Member('socrates','homem')

# classe Declaration
# -- associa um utilizador entity uma relacao por si inserida
#    na rede semantica
#
class Declaration:
    def __init__(self, user, rel):
        self.user = user
        self.relation = rel

    def __str__(self):
        return "decl(" + str(self.user) + "," + str(self.relation) + ")"

    def __repr__(self):
        return str(self)


#   Exemplos:
#   da = Declaration('descartes',entity)
#   ds = Declaration('darwin',s)
#   dm = Declaration('descartes',m)

# classe SemanticNetwork
# -- composta por um conjunto de declaracoes
#    armazenado na forma de uma lista
#
class SemanticNetwork:
    def __init__(self, ldecl=None):
        self.declarations = [] if ldecl is None else ldecl

    def __str__(self):
        return str(self.declarations)

    def insert(self, decl):
        self.declarations.append(decl)

    def query_local(self, user=None, e1=None, rel=None, rel_type=None, e2=None):
        self.query_result = \
            [d for d in self.declarations
             if (user is None or d.user == user)
             and (e1 is None or d.relation.entity1 == e1)
             and (rel is None or d.relation.name == rel)
             and (rel_type is None or isinstance(d.relation, rel_type))
             and (e2 is None or d.relation.entity2 == e2)]
        return self.query_result

    def show_query_result(self):
        for d in self.query_result:
            print(str(d))

    def list_associations(self) -> list:
        return list({d.relation.name for d in self.declarations if isinstance(d.relation, Association)})

    def list_objects(self) -> list:
        return list({d.relation.entity1 for d in self.declarations if isinstance(d.relation, Member)})

    def list_users(self) -> list:
        return list({d.user for d in self.declarations})

    def list_types(self) -> list:
        return list({d.relation.entity2 for d in self.declarations if
                     isinstance(d.relation, Member) or isinstance(d.relation, Subtype)})

    def list_local_associations(self, entity: str) -> list:
        return list({d.relation.name for d in self.declarations if
                     isinstance(d.relation, Association) and d.relation.entity1 == entity})

    def list_relations_by_user(self, user: str) -> list:
        return list({d.relation.name for d in self.declarations if d.user == user})

    def associations_by_user(self, user: str) -> int:
        return len(
            {d.relation.name for d in self.declarations if d.user == user and isinstance(d.relation, Association)})

    def list_local_associations_by_entity(self, entity: str) -> list:
        return list({(d.relation.name, d.user) for d in self.declarations if
                     d.relation.entity1 == entity and isinstance(d.relation, Association)})

    def predecessor(self, goal: str, start: str) -> bool:
        declarations_list = [d.relation for d in self.declarations if
                             (isinstance(d.relation, Member) or isinstance(d.relation, Subtype))
                             and d.relation.entity1 == start]

        if len(declarations_list) == 1 and declarations_list[0].entity2 == goal:
            return True

        return any([self.predecessor(goal, d.entity2) for d in declarations_list])

    def predecessor_path(self, a: str, b: str) -> list | None:
        decl = self.query_local(e1=b, rel_type=(Subtype, Member))
        print(f"\na = {a}, b = {b}")
        print(f"decl = {decl}")

        if len(decl) == 0:
            return None

        print(f"decl entity2 list = {[d.relation.entity2 for d in decl]}")
        if b in [d.relation.entity2 for d in decl]:
            return [b, a]

        for d in decl:
            if res := self.predecessor_path(b, d.relation.entity2):
                return res + [a]

    def query(self, entity: str, rel=None) -> list:
        decl_local = (self.query_local(e1=entity, rel=rel, rel_type=Association) +
                      self.query_local(e2=entity, rel=rel, rel_type=Association))

        pred_direct = self.query_local(e1=entity, rel_type=(Member, Subtype))

        decl = decl_local
        for dp in pred_direct:
            decl += self.query(dp.relation.entity2, rel)

        return decl

    def query2(self, entity: str, rel: str = None) -> list:
        decl_local = (self.query_local(e1=entity, rel=rel, rel_type=(Member, Subtype)) +
                      self.query_local(e2=entity, rel=rel, rel_type=(Member, Subtype)))

        return decl_local + self.query(entity, rel)

    def query_cancel(self, entity: str, rel: str) -> list:
        decl = (self.query_local(e1=entity, rel=rel, rel_type=Association) +
                self.query_local(e2=entity, rel=rel, rel_type=Association))
        decl_name = [d.relation.name for d in decl]

        for pd in self.query_local(e1=entity, rel_type=(Member, Subtype)):
            decl += [p for p in self.query_cancel(pd.relation.entity2, rel) if p.relation.name not in decl_name]

        return decl

    def query_down(self, tipo: str, assoc: str, first: bool = True) -> list:
        decl = ([] if first else self.query_local(e1=tipo, rel=assoc) + self.query_local(e2=tipo, rel=assoc))

        for dd in self.query_local(e2=tipo, rel_type=(Member, Subtype)):
            decl += [p for p in self.query_down(dd.relation.entity1, assoc, False)]
        return decl
