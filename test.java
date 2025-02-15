public class HelloWorld{
    public static void main(String[] args) {System.out.println("Hello World");int a = 10;for(int i=0;i<10;i++) {System.out.println(i);} while(a>0){a--;}do{a++;}while(a<10);}
    public void test(){System.out.println("Hello World");try{int x=1/0;}catch(Exception e){System.out.println(e.getMessage());}}
    public void test2() { if (true) {System.out.println("Hello World"); } else { System.out.println("Hello World"); } switch(a){case 1:{System.out.println("One");break;}default:System.out.println("Other");}}
    public void nestedLoops(){for(int i=0;i<5;i++){for(int j=0;j<5;j++){System.out.println(i*j);}}}
}

