from unittest import TestCase, main
from parameterized import parameterized
from pse.php_serialize_edit import (
    php_serialize, php_unserialize, Query, php_modify, ParseError
)


class TestPHPSerializeEdit(TestCase):
    @parameterized.expand([
        ["int", b"i:124;", 124],
        ["float", b"d:124.56;", 124.56],
        ["false", b"b:0;", False],
        ["true", b"b:1;", True],
        ["array1", b"a:2:{i:0;i:0;i:1;i:1;}", [(0, 0), (1, 1)]],
        ["array2", b'a:3:{i:0;a:2:{s:1:"a";b:1;s:1:"b";b:0;}i:1;i:0;i:2;i:1;}',
            [(0, [(b"a", True), (b"b", False)]), (1, 0), (2, 1)]],
        ["object1", b'O:6:"Person":2:{s:4:"name";s:4:"Jane";s:3:"age";i:25;}',
            (b"Person", [(b"name", b"Jane"), (b"age", 25)])],
    ])
    def test_php_unserialize(self, _name, serialized, expected):
        self.assertEqual(php_unserialize(serialized), expected)

    @parameterized.expand([
        ["int", b"i:124;"],
        ["float", b"d:124.56;"],
        ["false", b"b:0;"],
        ["true", b"b:1;"],
        ["array1", b"a:2:{i:0;i:0;i:1;i:1;}"],
        ["array2",
            b'a:3:{i:0;a:2:{s:1:"a";b:1;s:1:"b";b:0;}i:1;i:0;i:2;i:1;}'],
        ["object1", b'O:6:"Person":2:{s:4:"name";s:4:"Jane";s:3:"age";i:25;}'],
    ])
    def test_idempotence(self, _name, serialized):
        self.assertEqual(php_serialize(
            php_unserialize(serialized)), serialized)

    @parameterized.expand([
        ["get1", [(0, 0), (1, 1)], b"G:1", 1],
        ["get2", [(0, 0), (1, [(b"a", 10), (b"b", 12)])], b'G:1/"b"', 12],
        ["get3", 12.3, b"G:", 12.3],
        ["get4", 12.3, b"G:1", None],
        ["get5", [], b"G:1", None],
        ["get6", [], b"G:", []],
        ["get7", (b"Person", [(b"name", b"Jane"), (b"age", 25)]),
         b'G:"name"', b'Jane'],
        ["set1", [(0, 0), (1, 1)], b"S:2/1=3", [
            (0, 0), (1, 1), (2, [(1, 3)])]],
        ["set2", [(0, 0), (1, 1)], b"S:=3", 3],
        ["set3", [(0, 0), (1, 1)], b'S:="xyz"', b"xyz"],
        ["set4", [(0, 0), (1, 1)], b'S:0="xyz"', [(0, b"xyz"), (1, 1)]],
        ["set5", [(0, 0), (1, 1)], b"S:0=false", [(0, False), (1, 1)]],
        ["set6", [(0, 0), (1, 1)], b"S:1=true", [(0, 0), (1, True)]],
        ["set7", [(0, 0), (1, 1)], b"S:0=[0:0,1:1]", [(0, [(0, 0), (1, 1)]),
                                                      (1, 1)]],
        ["set8", None, b'S:=[["a":"b","c":"d"]:true]',
            [([(b"a", b"b"), (b"c", b"d")], True)]],
        ["set9", [(0, 0), (1, 1)], b"S:=3.3", 3.3],
        ["set10", [(3.3, 0), (1, 1)], b"S:3.3=1", [(3.3, 1), (1, 1)]],
        ["set11", (b"Person", [(b"name", b"Jane"), (b"age", 25)]),
         b'S:"name"="John"', (b"Person", [(b"name", b"John"), (b"age", 25)])],
        ["delete1", [(0, 0), (1, 1)], b"D:0", [(1, 1)]],
        ["delete2", [(0, 0), (1, [(b"a", 10), (b"b", 12)])], b'D:1/"b"',
         [(0, 0), (1, [(b"a", 10)])]],
        ["delete3", (b"Person", [(b"name", b"Jane"), (b"age", 25)]),
         b'D:"name"', (b"Person", [(b"age", 25)])],
    ])
    def test_query(self, _name, initial, expression, expected):
        self.assertEqual(Query(initial).run(expression), expected)

    @parameterized.expand([
        ["int", b"i:124;", b"S:=125", b"i:125;"],
        ["set", b"b:0;", b'S:=[["a":"b","c":"d"]:true]',
            b'a:1:{a:2:{s:1:"a";s:1:"b";s:1:"c";s:1:"d";}b:1;}'],
        ["array1", b"a:2:{i:0;i:0;i:1;i:1;}", b"D:1", b"a:1:{i:0;i:0;}"],
        ["array2",
            b'a:3:{i:0;a:2:{s:1:"a";b:1;s:1:"b";b:0;}i:1;i:0;i:2;i:1;}',
            b'S:0/"a"=12',
            b'a:3:{i:0;a:2:{s:1:"a";i:12;s:1:"b";b:0;}i:1;i:0;i:2;i:1;}'],
    ])
    def test_php_modify(self, _name, serialized, expression, expected):
        self.assertEqual(php_modify(serialized, expression), expected)

    @parameterized.expand([
        ["invalid_get1", b"G=123"],
        ["invalid_get2", b"G:123.abc"],
        ["invalid_set1", b"S:123=abc"],
        ["invalid_set2", b"S:key:value"],
        ["invalid_delete1", b"D:abc.def"],
        ["invalid_delete2", b"D:123 456"]
    ])
    def test_invalid(self, _name, expression):
        with self.assertRaises(ParseError):
            Query([]).run(expression)

    # These test strings are generated from the grammar by the
    # generate_grammar_valid_expression.py script
    @parameterized.expand([
        ["valid", b'D:-4118484.69601391321932/815066.373203'],
        ["valid", b'S:=-4507609.5472157063623'],
        ["valid", b'D:-0'],
        ["valid", b'G:"3A}YC_"/"GUGv!tRm,u?"/"RY+k~3}5z{S"/"C<0&p4,aWm8"/"tD1a!6J*n#]eI"'],
        ["valid", b'S:"Ky3,Ge-OF]"="8vtl2N o!nB-(`"'],
        ["valid", b'D:-961265617968832.093934/-4006735/85487734937'],
        ["valid", b'D:"4r"'],
        ["valid", b'G:"dN/\\\\)*C}Q;m\\\\v"'],
        ["valid", b'S:=68220622'],
        ["valid", b'D:"p`a80aZPP!U,QRM"'],
        ["valid", b'G:")fLs&$NPkj)"/29492614313842'],
        ["valid", b'D:-013377.0818'],
        ["valid", b'S:"y;"="|HOWA$4S"'],
        ["valid", b'D:"bxdS[z\\"$n"/715952/954667085920'],
        ["valid", b'D:"2#LzKMNd$5qo"/6109300064'],
        ["valid", b'S:=false'],
        ["valid", b'S:768246010998.6="9)[>, "'],
        ["valid", b'G:"Vn"/-7378862243365'],
        ["valid", b'D:"^-Wwf@7?Jkd5N"/"6+<~hW[aXI"'],
        ["valid", b'D:5607471924505/32109324463.723841730402'],
        ["valid", b'G:37'],
        ["valid", b'D:" -cL0;}"/"2Wh]]gZH"'],
        ["valid", b'D:"B~cL+Y=8"/"gt|gJ[2x6?6k\'%"/"yB|2gJ}4:=]>"'],
        ["valid", b'D:"\\\\}"/"{u|USymFF.p"'],
        ["valid", b'D:-825045289011.71629649054322'],
        ["valid", b'D:"Ri|}[-N"/";2 tcm|.,3"'],
        ["valid", b'D:"_Fc%d5"/-20163.588/5903378477/159579023720185/"}s-g0IW"'],
        ["valid", b'D:536949.2105259/"BVJsngY^3Gq`V"'],
        ["valid", b'S:-806019849199162=null'],
        ["valid", b'D:-06345'],
        ["valid", b'S:=-82'],
        ["valid", b'S:=-759469.4915057244947'],
        ["valid", b'D:490433942/"^ILmzJ!$"'],
        ["valid", b'D:"g,pSSOe|&"'],
        ["valid", b'S:=">/X%M"'],
        ["valid", b'D:959436/"Uc\'&#KrkafV;"/"9_"/"qAeJB2PC$:=\'qE"'],
        ["valid", b'D:"m_/,/y!ylsL"/"2dAt#jZ"'],
        ["valid", b'S:"<y!"="tlHetRoFe *E["'],
        ["valid", b'D:-984.85'],
        ["valid", b'D:"#r-YWhl"/4.04922398298186'],
        ["valid", b'G:"U8:&<#/(-7YnHNx"'],
        ["valid", b'G:158306.804158812095/"5xKjnY"'],
        ["valid", b'D:"Je)/$Geq]i"'],
        ["valid", b'S:"-@p2|C*=\\"Gf"="d"'],
        ["valid", b'S:=true'],
        ["valid", b'S:"Kep3"=-292768'],
        ["valid", b'D:"\\"J:AB^<NOu/V9b"/-9169734722504'],
        ["valid", b'S:="&_\\"27w$C56YD+"'],
        ["valid", b'G:051.312621948450/-3577269721/-52504.91'],
        ["valid", b'D:9817.8184/-590116122643.9653302268806'],
        ["valid", b'D:"HL=L>4]d`6l"/342243234880/"`^P\'2UcbD=2L&"'],
        ["valid", b'D:71/610104576330447./"Xu<AV~b_ln&8jR"/-7659.'],
        ["valid", b'S:="Wyqr_dhL"'],
        ["valid", b'G:'],
        ["valid", b'G:-8666936/5705859/1'],
        ["valid", b'D:"a]@Q6BbGUX"'],
        ["valid", b'G:"e*nKy"'],
        ["valid", b'G:3'],
        ["valid", b'D:776982/"Ec@*%34*Xy>,"/-3485.3'],
        ["valid", b'G:"fsOndFw^a2q("'],
        ["valid", b'D:"jvLA1*S*x"'],
        ["valid", b'S:-323771256563419=31.812225636777'],
        ["valid", b'D:-3/"+/Zi"'],
        ["valid", b'S:=75301350'],
        ["valid", b'D:"cFh"'],
        ["valid", b'G:26281995254119.'],
        ["valid", b'S:=null'],
        ["valid", b'D:512012.2649/-70974306.6773470658'],
        ["valid", b'D:"AYOd3j!"'],
        ["valid", b'G:-349321077'],
        ["valid", b'S:665640571290576.014155686/7326426="r2\\\\"'],
        ["valid", b'D:"!Sc,q$QBWa/e"/904253012969'],
        ["valid", b'S:-129878783414.3831/"4X8*1aX~^"/"G^Ij)HFXh%"/"m5>L}U` F"/"u9^l>F"=false'],
        ["valid", b'S:-57639233.312775344572/1.137=true'],
        ["valid", b'G:-590000143.90735/"7[["/"f0"/"G<6"'],
        ["valid", b'D:"EHv~(f%_SwsjDu"/"A"'],
    ])
    def test_valid(self, _name, expression):
        try:
            Query([]).run(expression)
        except ParseError as e:
            raise AssertionError(f'Error on {expression}: {e}')
    @parameterized.expand([
        ["invalid", b'G:"abc\\'],
        ["invalid", b'x '],
        ["invalid", b'D:x1 xx8 5 99713'],
        ["invalid", b':"  3/  " dQ  R}h% A} ^xxx/ $ xxI x\'[ xx'],
        ["invalid", b':-x 9x6 4 8 19'],
        ["invalid", b': "x R[d H " '],
        ["invalid", b'S: 04  4x 5x2 2/ "  lA x "= ""'],
        ["invalid", b'S: p j x7  WD#  : ? "x fmxeU  x ] o Sy  =; W >xZm x'],
        ["invalid", b' D:" A<Y  IH x 6'],
        ["invalid", b'D:B p n8zIx/  74x 1546 4xx'],
        ["invalid", b'Dx\\ wZ "/ 39 4xx298  010" r " '],
        ["invalid", b'x- 94x9  904 6 2 x 15xx 5'],
        ["invalid", b'D:  q /> 2 _ xxW e" '],
        ["invalid", b'D: 36x2  2xx 587 81xxx097" L '],
        ["invalid", b'S = null'],
        ["invalid", b'Da H>  MY U "  95  234 47x'],
        ["invalid", b'G: '],
        ["invalid", b'Dx 233 8 5'],
        ["invalid", b':x2 x2 x./ x7x07x61 x0  7 32 67'],
        ["invalid", b' S: null '],
        ["invalid", b'S:  "# xfx];X G " "k"'],
        ["invalid", b' S: 2 3.  76x 1x/ *Bs c2 x[xa x 54  6 2 52  33  7x1 64 9 x 0 8 1 2x/ - = " s Q 7 Xxn ~x" '],
        ["invalid", b' G:" =E  3 }</1 xx4 x49  45 8 60 4 9 65 /" ""  >x'],
        ["invalid", b':x3 x30 x 53 '],
        ["invalid", b'x83. 8  71 41  40 9 / 3  77 x6 8 3'],
        ["invalid", b'D:h\\\\$ >Usxx ex? xxx. 8  3x 95  / -70 x 4 7 274 x08 2 xx/  3 1 33  59 x9 0 4 '],
        ["invalid", b'xx6 9 2  7 7x6 79 . /x Jx:t" x "xF  bO " '],
        ["invalid", b' D:" |/  ox5x \\\\" '],
        ["invalid", b'x "7 l fxxxx\\xx :t  gx "'],
        ["invalid", b'x28 67 3  8 0x38 '],
        ["invalid", b'x " k| ^ x ) 2e  "'],
        ["invalid", b'S:" x5 9xx7  65 56 79 5 9 9 5x 93x " C \'\\x!   null'],
        ["invalid", b'xxx$ m; wx; " Xx^ x"xx V7U bk 9 1"xx;  * (" "  wJ L}C  Qa  P 0f x "'],
        ["invalid", b'Gx'],
        ["invalid", b' D: 7xx1 8x8xx29 5 2x1x /"W7  x" x"x q |^ Y  ^ "/ x6  ~q N j   ! "- 8x 0 2x8  5. 7xx6  5x 3'],
        ["invalid", b' S:1 x8  60  = -43 4 6  9'],
        ["invalid", b':8  2 79x2 xx 92 '],
        ["invalid", b'S:=fals'],
        ["invalid", b'D:" x31  ,q xxS 6 /x7] 4 Cn x" s xS [S '],
        ["invalid", b'D: 6 702 6 0 x'],
        ["invalid", b': 1 '],
        ["invalid", b' G:x'],
        ["invalid", b' D:x7 x 44  /V x }  *x" / "  n2 m o" @> @n m 0 \\"/  " 35x 91 9'],
        ["invalid", b' G: '],
        ["invalid", b'G:1 92 1 818 4 '],
        ["invalid", b'D "< Zv!xxx 6x /x9Fxx\\x u@&a '],
        ["invalid", b'D:" P  c^ 7\\" $p" '],
        ["invalid", b'Gx 0 2x3 6 36  .535  51 '],
        ["invalid", b'xx1 xvxZsx O /7 6 / + ox01x 9 4 3 5xx 08 -22 2 8 9 9x/ "x?  8x= Qx / 4x0 30x 5 8 90  05 5xx 5x9 0x; G" '],
        ["invalid", b' G:x2  8?  ,x- ^/<x2d "/99 93 5 110x 83 0. x6 6 7 x'],
        ["invalid", b': 358 42 . 1xxx7 ]NMm x6x-  01  7 8 84  71/9  5x07  58 2'],
        ["invalid", b':xp  rG  ~ Mx frxxI" - 437 x.4  3x56xx'],
        ["invalid", b'Sx8 7  0 9x 4xx = false'],
        ["invalid", b'S:  = x'],
        ["invalid", b'D: 60 2 498  9 2'],
        ["invalid", b'G'],
        ["invalid", b': . 5 60 '],
        ["invalid", b'G:x'],
        ["invalid", b'x- x = "x0 Fv6 M 4J'],
        ["invalid", b':'],
        ["invalid", b':" px; xx'],
        ["invalid", b':"  q  {%'],
        ["invalid", b'G" xHx t0xx'],
        ["invalid", b' G:-xx 3 30  4xx/xx) N/ Um xo x'],
        ["invalid", b':"8x1 xxxx r.d   x'],
        ["invalid", b'G:  "xw cx\\'],
        ["invalid", b'G 5.x 97 '],
        ["invalid", b' G:'],
        ["invalid", b' G:9 1 '],
        ["invalid", b'G: Z5 8xx7 x80x4xx6 7 64'],
        ["invalid", b':" /"'],
        ["invalid", b'x"JkJ \\"  -x=x  . "/ Z /@?~ < x$ "x }x Yx. x\\" G '],
        ["invalid", b'S-  2x1x .2 9 x0 3x 32 3 x s"  = -8 91x78 x'],
        ["invalid", b' G: 07 x 7 8xx 4x6.  9 1 76. 7 " Ldxx-8 08 x 70 9'],
        ["invalid", b'x'],
        ["invalid", b' D:xD< '],
        ["invalid", b'Dx1 0xx3 1 29x4  1-1 6x0xx5 x65 '],
        ["invalid", b'D:"x\\" y # xxxx +7'],
        ["invalid", b'S:  =-x'],
        ["invalid", b'x4xx6 x2 6 48  87 5 6  3837 4xx6 x 4x2 0 4  9x 9x58 x /7  40  8x/ p h$ K +0 > xR bx" /x* \\" ;  nz R "x'],
        ["invalid", b':xtrue'],
        ["invalid", b'D: " xC  PX "  "M \\P u\\\\xYxx3 NY x/ -0xxx6x2 6 7xxxxxx1xx U'],
        ["invalid", b'G- 5 x3 xxx3  9x7 7 0/96 2  5 37x6  /x14 2x'],
        ["invalid", b'S:6 87 31  4x3  5xx7 6 x5 9x34 6 x 2 .4 3 x= false'],
        ["invalid", b'x"  % 8xxx#Ox//  -643x0 10 53/xxx4 3 5 .9 2 4 9 56  45 0 8/  "x'],
        ["invalid", b': '],
        ["invalid", b'D 3 14 " ,"" 5  iV (vxx & %"x " ~ s\'xh2 x = / - 8 98 2 xxx'],
        ["invalid", b' G:x9 x9x4 x70. 4x 1 /xxE c +x/ ") "- 9 9 2.58x2 99 '],
    ])
    def test_invalid(self, _name, expression):
        with self.assertRaises(ParseError):
            Query([]).run(expression)


if __name__ == '__main__':
    main()
