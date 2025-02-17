public class hello_World
{
    public static final String name = "hello_world";

    int name_this_day = 0;
    public static void main(String[] args)
    {
        hello_world instance = new hello_world();
        instance.test_that();
        instance.test_that_2(5);
        instance.Nested_loops();

        System.out.println(instance.test_that_2(5));
        System.out.println("Hello World");
        int a = 10;
        name_this_day++;
        for(int i=0;i<10;i++)
        {
            System.out.println(i);
        }
        while(a>0)
        {
            a--;
        }
        do
        {
            a++;
        }while(a<10);
    }

    public void test_that()
    {
        System.out.println("Hello World");
        try
        {
        int x=1/0;
        }catch(Exception e)
        {
    System.out.println(e.getMessage());System.out.println(test_that_2());
        }
    }

    public void test_that_2(int one_one)
{        if (true)
       {            one_one=1;
        System.out.println("Hello World");
    } else        {
          System.out.println("Hello_World");
    }
    switch(a)
        {
            case 1:
                {
                    System.out.println("One");
                    break;
                }
            default:
                System.out.println("Other");
        }
    }

    public void Nested_loops()
    {
        for(int I=0;i<5;i++)
        {
            for(int J=0;j<5;j++)
            {
                System.out.println(I*J);
            }
        }
    }
}
// test_that()

class another_class {
    public static void main(String[] args) {
        hello_world instance = new hello_world();
        System.out.println(instance.test_that_2(5));
    }
}