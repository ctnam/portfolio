/**
 * DOC
 * methods send, transmitMessage, reply: operations of a messaging process
 */

interface Messagable {
    void send (String message);
    void transmitMessage (String message);
    default void reply () {};
}
