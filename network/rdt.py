import socket
import random
import time
import logging
import select
import hashlib
from utils.config import TIMEOUT, LOSS_PROBABILITY

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class RDT:
    def __init__(self, sock, remote_addr):
        self.sock = sock
        self.remote_addr = remote_addr
        self.seq_num = 0  # 0 ou 1
        self.timeout = TIMEOUT

    def _calculate_checksum(self, data):
        """Calcula checksum MD5 (4 bytes)"""
        return hashlib.md5(data).digest()[:4]

    def _make_packet(self, data):
        """Cria pacote: seq(1) + checksum(4) + data"""
        seq_byte = self.seq_num.to_bytes(1, 'big')
        checksum = self._calculate_checksum(seq_byte + data)
        return seq_byte + checksum + data

    def parse_packet(self, packet):
        """Método público para parsear pacote RDT"""
        if len(packet) < 5:
            return None, None, False
        
        seq = packet[0]
        received_checksum = packet[1:5]
        data = packet[5:]
        
        # Verifica checksum
        seq_byte = seq.to_bytes(1, 'big')
        calculated_checksum = self._calculate_checksum(seq_byte + data)
        
        checksum_ok = (received_checksum == calculated_checksum)
        
        return seq, data, checksum_ok

    def _send_with_loss(self, packet):
        """Simula perda de pacotes com probabilidade configurável"""
        if random.random() < LOSS_PROBABILITY:
            logging.info(f"[RDT] Pacote (seq={self.seq_num}) SIMULADO como PERDIDO!")
            return False
        try:
            sent = self.sock.sendto(packet, self.remote_addr)
            logging.info(f"[RDT] Enviado pacote (seq={self.seq_num}, {sent} bytes)")
            return True
        except Exception as e:
            logging.error(f"[RDT] Erro ao enviar: {e}")
            return False

    def send(self, data):
        """Envia dados usando RDT 3.0 (com ACK e timeout)"""
        if not isinstance(data, bytes):
            data = data.encode()
            
        tentativas = 0
        max_tentativas = 10
        
        logging.debug(f"[RDT] Iniciando envio de {len(data)} bytes, seq={self.seq_num}")
        
        while tentativas < max_tentativas:
            tentativas += 1
            packet = self._make_packet(data)
            
            # Enviar pacote (com possível perda)
            if not self._send_with_loss(packet):
                # Se o pacote foi "perdido" na simulação, espera timeout
                logging.info(f"[RDT] Pacote perdido (simulação), tentativa {tentativas}")
                time.sleep(self.timeout)  # Espera pelo timeout
                continue
            
            # Pacote enviado, espera ACK
            logging.debug(f"[RDT] Aguardando ACK para seq={self.seq_num}, tentativa {tentativas}")
            
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    # Usar select para verificar se há dados disponíveis
                    ready = select.select([self.sock], [], [], 0.1)
                    if ready[0]:
                        ack_data, addr = self.sock.recvfrom(1024)
                        
                        # Verificar se é do endereço correto
                        if addr != self.remote_addr:
                            logging.debug(f"[RDT] ACK de endereço errado: {addr}")
                            continue
                            
                        # ACK é apenas o número de sequência (1 byte)
                        if len(ack_data) == 1:
                            ack_seq = ack_data[0]
                            if ack_seq == self.seq_num:
                                logging.info(f"[RDT] ACK recebido para seq={self.seq_num}")
                                self.seq_num = 1 - self.seq_num  # Alternar seq_num
                                return
                            else:
                                logging.debug(f"[RDT] ACK com seq errado: {ack_seq}, esperado: {self.seq_num}")
                        else:
                            logging.debug(f"[RDT] ACK com tamanho inválido: {len(ack_data)} bytes")
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    logging.error(f"[RDT] Erro recebendo ACK: {e}")
                    break
            
            logging.warning(f"[RDT] Timeout! Retransmitindo (seq={self.seq_num}, tentativa {tentativas})")
        
        # Se chegou aqui, excedeu o número máximo de tentativas
        raise Exception(f"Falha ao enviar após {max_tentativas} tentativas")

    def recv(self):
        """Recebe dados usando RDT 3.0"""
        while True:
            try:
                logging.debug(f"[RDT] Aguardando dados, esperando seq={self.seq_num}")
                
                # Receber pacote
                packet, addr = self.sock.recvfrom(1024)
                
                # Verificar se é do endereço correto
                if addr != self.remote_addr:
                    logging.debug(f"[RDT] Pacote de endereço errado: {addr}")
                    continue
                
                # Parsear pacote
                seq, data, checksum_ok = self.parse_packet(packet)
                
                if seq is None:
                    logging.debug("[RDT] Pacote inválido, ignorando")
                    continue
                
                logging.debug(f"[RDT] Pacote recebido: seq={seq}, checksum_ok={checksum_ok}, data_len={len(data)}")
                
                # Enviar ACK (apenas o número de sequência)
                ack_packet = seq.to_bytes(1, 'big')
                try:
                    self.sock.sendto(ack_packet, addr)
                    logging.debug(f"[RDT] ACK enviado para seq={seq}")
                except Exception as e:
                    logging.error(f"[RDT] Erro enviando ACK: {e}")
                
                # Processar dados se checksum OK e seq correto
                if checksum_ok and seq == self.seq_num:
                    logging.info(f"[RDT] Pacote aceito: seq={seq}")
                    self.seq_num = 1 - self.seq_num  # Alternar seq_num
                    return data
                else:
                    if not checksum_ok:
                        logging.info(f"[RDT] Pacote com checksum errado descartado (seq={seq})")
                    else:
                        logging.info(f"[RDT] Pacote duplicado (seq={seq}), ignorado")
                        
            except Exception as e:
                logging.error(f"[RDT] Erro na recepção: {e}")
                raise