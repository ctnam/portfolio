/**
 * DOC
 * method run corresponds to the task of 2 players communicating with each other - initiator1 identifies the recipient then sending the message, while receiver1 replies
 */

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

//5. both players should run in the same java process (strong requirement)
public class JunctionProcess {
    static ExecutorService executor = Executors.newSingleThreadExecutor();
    static List<Player> playerList = Player.newInstances("initiator1", "receiver1");  //1. create 2 Player instances
    static {System.out.println("Same process with Hello");}
    
    public static void run () {
        executor.submit(new Runnable () {
            @Override
            public void run() {
                //2. one of the players should send a message to second player (let's call this player "initiator")
                playerList.get(0).initiateToRecipient(playerList.get(1)).send("Hallo ");
            }
        });
        executor.close();
    }
}
