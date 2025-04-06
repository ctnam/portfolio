/**
 * DOC
 * initiateToRecipient: one player self-identified as sender identifies the recipient, which makes himself/herself the initiator
 * send: sets the stop condition, identifies the message, forwarding to sendLog and transmitMessage
 * reply: forwards to send after setting the recipient
 * transmitMessage: sets the message to recipient, saves the counters, forwarding to reply
 * sendLog: prints out the sending to console
 */

import java.util.List;
import java.util.stream.Stream;

class Player implements Initiator<Player>, Messagable {
    private boolean replyMode = true;
    private byte sentCounter, receivedCounter;
    private final String name;
    private Player sender, recipient;
    private static Player initiator;
    private String sendMessage, receiveMessage;

    private Player (final String name) {this.name = name;}
    public static Player newInstance (final String name) {return new Player(name);}
    public static List<Player> newInstances (final String... names) {return Stream.of(names).map(Player::newInstance).toList();}

    @Override
    public Player initiateToRecipient (Player recipient) {
        this.recipient = recipient;
        recipient.sender = this;
        initiator = this;
        return this;
    }

    //2. one of the players should send a message to second player (let's call this player "initiator")
    @Override
    synchronized public void send (String sendMessage) {
        //4. finalize the program (gracefully) after the initiator sent 10 messages and received back 10 messages (stop condition)
        if (!(initiator.sentCounter == 10 && initiator.receivedCounter == 10)) {
                    this.sendMessage = sendMessage;
                    sendLog(this, recipient, sendMessage);
                    transmitMessage(sendMessage);
        }
    }

    //3. when a player receives a message, it should reply with a message that contains the received message concatenated with the value of a counter holding the number of messages this player already sent.
    @Override
    public void reply () {
        recipient = sender;
        recipient.sender = this;
        send(new StringBuffer(receiveMessage).append(sentCounter).toString());
    }

    //3. when a player receives a message, it should reply with a message that contains the received message concatenated with the value of a counter holding the number of messages this player already sent.
    @Override
    public void transmitMessage (String transmitMessage) {
        recipient.receiveMessage = transmitMessage;  
        sentCounter++;
        recipient.receivedCounter++;
        if (recipient.replyMode) recipient.reply();
    }

    public void activateReply () {if (!replyMode) replyMode = true;}

    protected void sendLog (Player sender, Player recipient, String message) {
        System.out.printf("From %s to %s: %s %n", sender, recipient, message);
    }

    @Override
    public String toString () {return name;}
}

