/**
 * DOC
 * methods run1, run2 correspond to 2 tasks: one is to activate the reply mode by receiver2, and another one is to identify the recipient then sending the message by initiator2
 */

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

//7. additional challenge (nice to have) opposite to 5: have every player in a separate JAVA process.
public class SeparateProcess {
    static ExecutorService executor = Executors.newFixedThreadPool(2);
    static Player initiator2 = Player.newInstance("initiator2");
    static Player receiver2 = Player.newInstance("receiver2");
    static {System.out.println("Separate process with Hi");}

    public static void run1 () {
        executor.submit(new Runnable () {
            @Override
            public void run() {
                receiver2.activateReply();
            }
        });
    }

    public static void run2 () {
        executor.submit(new Runnable () {
            @Override
            public void run() {
                initiator2.initiateToRecipient(receiver2).send("Hi ");
            }
        });
        executor.close();
    }
}
 