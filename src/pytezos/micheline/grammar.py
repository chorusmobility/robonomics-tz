# -*- coding: utf-8 -*-

from ply.lex import Lexer, lex
from ply.yacc import yacc
import re

# Inspired by https://github.com/jansorg/tezos-intellij/blob/master/grammar/michelson.bnf


class SimpleMichelsonLexer(Lexer):
    tokens = (
        'PRIM', 'INT', 'BYTE', 'STR',
        'LEFT_CURLY', 'RIGHT_CURLY', 'LEFT_PAREN', 'RIGHT_PAREN', 'SEMI',
        'COMMENT', 'MULTI_COMMENT', 'ANNOT'
    )
    t_PRIM = r'[A-Za-z_]+'
    t_INT = r'-?[0-9]+'
    t_BYTE = r'0x[A-Fa-f0-9]+'
    t_STR = r'\"[^\"]*\"'
    t_LEFT_CURLY = r'\{'
    t_RIGHT_CURLY = r'\}'
    t_LEFT_PAREN = r'\('
    t_RIGHT_PAREN = r'\)'
    t_SEMI = r';'
    t_COMMENT = r'#[^\n]+'
    t_MULTI_COMMENT = r'/"\* ~\*"/'
    t_ANNOT = r'[:@%](@|%|%%|[_a-zA-Z][_0-9a-zA-Z\.]*)?'
    t_ignore = ' \r\n\t\f'

    def __init__(self):
        super(SimpleMichelsonLexer, self).__init__()
        self.lexer = lex(module=self, reflags=re.DOTALL)


class MichelineParser(object):
    tokens = SimpleMichelsonLexer.tokens

    def p_instr(self, p):
        '''instr : expr
                 | empty
        '''
        p[0] = p[1]

    def p_instr_list(self, p):
        '''instr : instr SEMI instr'''
        p[0] = list()
        for i in [p[1], p[3]]:
            if isinstance(i, list):
                p[0].extend(i)
            elif i is not None:
                p[0].append(i)

    def p_instr_subseq(self, p):
        '''instr : LEFT_CURLY instr RIGHT_CURLY'''
        p[0] = list()
        if p[2] is not None:
            p[0].append(p[2])

    def p_expr(self, p):
        '''expr : PRIM annots args'''
        p[0] = {'prim': p[1]}
        if p[2]:
            p[0]['annots'] = p[2]
        if p[3]:
            p[0]['args'] = p[3]

    def p_annots(self, p):
        '''annots : annot
                  | empty
        '''
        if p[1] is not None:
            p[0] = [p[1]]

    def p_annots_list(self, p):
        '''annots : annots annot'''
        p[0] = list()
        if isinstance(p[1], list):
            p[0].extend(p[1])
        if p[2] is not None:
            p[0].append(p[2])

    def p_annot(self, p):
        '''annot : ANNOT'''
        p[0] = p[1]

    def p_args(self, p):
        '''args : arg
                | empty
        '''
        p[0] = list()
        if p[1] is not None:
            p[0].append(p[1])

    def p_args_list(self, p):
        '''args : args arg'''
        p[0] = list()
        if isinstance(p[1], list):
            p[0].extend(p[1])
        if p[2] is not None:
            p[0].append(p[2])

    def p_arg_prim(self, p):
        '''arg : PRIM'''
        p[0] = {'prim': p[1]}

    def p_arg_int(self, p):
        '''arg : INT'''
        p[0] = {'int': p[1]}

    def p_arg_byte(self, p):
        '''arg : BYTE'''
        p[0] = {'bytes': p[1][2:]}  # strip 0x prefix

    def p_arg_str(self, p):
        '''arg : STR'''
        p[0] = {'string': p[1].strip('"')}

    def p_arg_subseq(self, p):
        '''arg : LEFT_CURLY instr RIGHT_CURLY'''
        if isinstance(p[2], list):
            p[0] = p[2]
        elif p[2] is not None:
            p[0] = [p[2]]
        else:
            p[0] = []

    def p_arg_group(self, p):
        '''arg : LEFT_PAREN expr RIGHT_PAREN'''
        p[0] = p[2]

    def p_empty(self, p):
        '''empty :'''

    def __init__(self, debug=False, write_tables=False):
        self.lexer = SimpleMichelsonLexer()
        self.parser = yacc(
            module=self,
            debug=debug,
            write_tables=write_tables,
        )

    def parse(self, code):
        return self.parser.parse(code)
