def link_to_sender_receiver(link):
    link = link.split("\'")

    sender = link[1]
    receiver = link[3]

    return sender, receiver

def parse_link_to_ints(link):
    sender = int(link[0].split(".")[0], 10)
    receiver = int(link[1].split(".")[0], 10)

    return sender, receiver

def parse_link_ints_to_str(link):
    sender_id, receiver_id = link
    return f"{sender_id}.Out", f"{receiver_id}.In"